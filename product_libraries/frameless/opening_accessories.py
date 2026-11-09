"""3D models for the catalog accessories kept on a frameless opening.

Accessories added to a door or open opening (or a division section) are
ACCESSORY items on that cage (interior_items.accessory_host). The face
frame library already turns those items into units: a product entry
that names a model builds it (pull-outs, roll-out trays, organizers,
swing racks, blind corner swing-outs...), racks that mount on a door are
built on the door's back, and an accessory with no model shows its name
as a text label in the opening. This module runs the same descriptors
and mesh builders for frameless cages.

The opening rect is the cage itself (frameless has no face frame): a
hinged side keeps the same clearance the interior items take, and a
blind corner's blind span counts as the reveal on its blind side, which
is how the swing-out models find the blind side.

Units in the opening are parented to the host cage; door racks are
parented to their door with the door's closed transform as the parent
inverse, so they swing with it. Neither is a cutpart. Everything is
rebuilt only when its signature changes.
"""

import math

import bpy
from mathutils import Euler, Matrix, Vector

from ...units import inch
from . import solver_frameless as sf

MODEL_TAG = 'IS_FRAMELESS_ACCESSORY_MODEL'
HOST_KEY = 'hb_accessory_host'
SIGNATURE_KEY = 'hb_accessory_model_signature'
COUNT_KEY = 'hb_accessory_model_count'
MENU_ID = 'HOME_BUILDER_MT_interior_part_commands'

_HOST_TAGS = ('IS_FRAMELESS_OPENING_CAGE', 'IS_FRAMELESS_BAY_CAGE',
              'IS_FRAMELESS_INTERIOR_SECTION')
_INSERT_TAGS = ('IS_FRAMELESS_OPENING_CAGE', 'IS_FRAMELESS_BAY_CAGE')
_DOOR_ROLES = ('LEFT_DOOR', 'RIGHT_DOOR')
_HINGE_NAMES = {sf.SWING_LEFT: 'LEFT', sf.SWING_RIGHT: 'RIGHT',
                sf.SWING_DOUBLE: 'DOUBLE'}

_SOLVING = set()


def _ff():
    from ..face_frame import (accessory_models, corner_accessory_models,
                              misc_accessory_models, solver_face_frame)
    return (accessory_models, corner_accessory_models,
            misc_accessory_models, solver_face_frame)


def _items():
    from . import interior_items
    return interior_items


# ---------------------------------------------------------------------------
# Where the units go
# ---------------------------------------------------------------------------

def _insert_and_offset(host):
    """The opening or bay cage holding ``host`` (``host`` itself when it
    is one) and ``host``'s origin in that cage's frame."""
    offset = Vector((0.0, 0.0, 0.0))
    obj = host
    while obj is not None and not any(obj.get(t) for t in _INSERT_TAGS):
        offset += obj.location
        obj = obj.parent
    return obj, offset


def _rect(host, insert, offset):
    """(model rect, label rect, x shift) for ``host``. The rect is the
    face frame item rules' one: the cage size with hinge clearance as
    side reveals. A blind corner's door bay stops at the blind panel, so
    for the models the rect reaches on over the blind span, which counts
    as the reveal on that side (how the swing-outs find the blind side);
    the shift brings positions in that wider rect back to the cage."""
    ii = _items()
    dim_x, dim_y, dim_z = sf.cage_dims(host)
    left, right = ii._hinge_sides(insert)
    pocket_l, pocket_r = sf.pocket_sides(insert)
    if pocket_l:
        left = sf.POCKET_WIDTH
    if pocket_r:
        right = sf.POCKET_WIDTH
    blind = None
    if host is not insert:
        tol = inch(0.01)
        if offset.x > tol:
            left = 0.0
        if offset.x + dim_x < sf.cage_dims(insert)[0] - tol:
            right = 0.0
    else:
        blind = sf.blind_reach(insert)
    rect = {'cage_dim_x': dim_x, 'cage_dim_y': dim_y, 'cage_dim_z': dim_z,
            'reveal_left': left, 'reveal_right': right,
            'reveal_top': 0.0, 'reveal_bottom': 0.0}
    if blind is None:
        return rect, rect, 0.0
    span, on_left, _panel_t = blind
    wide = dict(rect, cage_dim_x=dim_x + span)
    if on_left:
        wide['reveal_left'] = span
        return wide, rect, -span
    wide['reveal_right'] = span
    return wide, rect, 0.0


def _swing(insert):
    """(door angle, hinge side name) for swing-rack models."""
    if insert is None or 'Door Swing' not in insert:
        return 0.0, 'RIGHT'
    amount = sf.open_amount(insert) if sf.OPEN_KEY in insert else 0.0
    swing = int(sf.prompt(insert, 'Door Swing', sf.SWING_DOUBLE))
    return amount * sf.DOOR_MAX_SWING, _HINGE_NAMES.get(swing, 'RIGHT')


def _opening_descriptors(host, insert, rects, items):
    """One descriptor per accessory: its model, or its text label."""
    am, cam, _misc, sff = _ff()
    rect, label_rect, shift = rects
    front_y, back = sff.BAR_STORAGE_FRONT_Y, sff.SHELF_BACK_SETBACK
    dim_y = rect['cage_dim_y']
    out = []
    for item in items:
        desc = am.descriptor(rect, dim_y, item, front_y, back)
        if desc is None:
            desc = cam.descriptor(rect, dim_y, item, front_y, back)
        if desc is None:
            out.append(sff._accessory_label_descriptor(
                label_rect, dim_y, item.accessory_label,
                item.accessory_label or item.accessory_code))
            continue
        if shift:
            x, y, z = desc['position']
            desc['position'] = (x + shift, y, z)
        params = desc.get('params')
        if isinstance(params, dict) and '_swing' in params:
            params['_swing'], params['_hinge'] = _swing(insert)
        out.append(desc)
    return out


# ---------------------------------------------------------------------------
# Door racks
# ---------------------------------------------------------------------------

def _doors(insert):
    doors = [c for c in insert.children
             if c.get('IS_CABINET_FRONT')
             and c.get(sf.PART_ROLE_KEY) in _DOOR_ROLES
             and not c.hide_viewport]
    doors.sort(key=lambda d: _DOOR_ROLES.index(d.get(sf.PART_ROLE_KEY)))
    return doors


def _door_closed(insert, door):
    """(closed local matrix, closed back-face y, x span) of a door in its
    insert's frame."""
    from ...hb_types import GeoNodeCutpart
    dim_x = sf.cage_dims(insert)[0]
    _top, bottom, left, right = sf.front_overlays(insert)
    thickness = float(sf.prompt(insert, 'Front Thickness', inch(0.75)))
    if insert.get('Inset Front', False):
        y = thickness
    else:
        y = -float(sf.prompt(insert, 'Door to Cabinet Gap', inch(0.125)))
    width = float(GeoNodeCutpart(door).get_input('Width'))
    if door.get(sf.PART_ROLE_KEY) == 'LEFT_DOOR':
        loc = Vector((-left, y, -bottom))
        span = (-left, -left + width)
    else:
        loc = Vector((dim_x + right, y, -bottom))
        span = (dim_x + right - width, dim_x + right)
    if sf.OPEN_KEY in insert and sf.open_amount(insert) > 0.0:
        closed = Matrix.LocRotScale(loc, Euler(sf._FRONT_ROTATION), None)
    else:
        closed = door.matrix_basis.copy()
    return closed, y, span


def _door_rack_specs(insert, items):
    """[(item, entry, model, params, margin, door)] for the racks the
    accessories hang on doors."""
    _am, _cam, misc, _sff = _ff()
    doors = _doors(insert)
    out = []
    for item in items:
        spec = misc._front_spec(getattr(item, 'accessory_code', ''))
        if spec is None or not doors:
            continue
        entry, model, params = spec
        if model not in misc.DOOR_RACK_MODELS:
            continue
        targets = list(doors)
        if model == 'door_rack':
            if getattr(item, 'accessory_door', 'LEFT') == 'RIGHT':
                targets.reverse()
            targets = targets[:max(getattr(item, 'accessory_qty', 1), 1)]
        rparams = dict(params)
        if model == 'swinger_pantry':
            rparams = {'rack_depth': params.get('door_rack_depth', 4.0),
                       'spacing': params.get('door_rack_spacing', 12.0),
                       'rails': 'chrome'}
        margin = inch(misc._f(params, 'side_margin', 1.5))
        for door in targets:
            out.append((item, entry, rparams, margin, door))
    return out


def _rack_placement(insert, door, params, margin):
    """(closed door matrix, position, (w, d, h)) of a rack in the
    insert's frame, or None when the door leaves no room."""
    _am, _cam, misc, _sff = _ff()
    dim_x, _dim_y, dim_z = sf.cage_dims(insert)
    closed, back_y, (dx0, dx1) = _door_closed(insert, door)
    x0 = max(0.0, dx0) + margin
    x1 = min(dim_x, dx1) - margin
    z0, z1 = inch(0.5), dim_z - inch(0.5)
    w, h = x1 - x0, z1 - z0
    if w < inch(2.0) or h < inch(1.0):
        return None
    d = inch(misc._f(params, 'rack_depth', misc._f(params, 'tray_depth', 4.0)))
    return closed, (x0, back_y + inch(0.0625), z0), (w, d, h)


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

def _link(obj, host):
    for coll in host.users_collection:
        coll.objects.link(obj)
        return
    bpy.context.scene.collection.objects.link(obj)


def _tag(obj, host, role):
    obj[MODEL_TAG] = True
    obj[HOST_KEY] = host.name
    obj[sf.PART_ROLE_KEY] = role
    obj['MENU_ID'] = MENU_ID


def _build_label(host, desc):
    from ...hb_details import apply_label_style
    _am, _cam, _misc, sff = _ff()
    curve = bpy.data.curves.new(type='FONT', name=desc['name'])
    curve.body = desc['text']
    curve.size = desc['size']
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    obj = bpy.data.objects.new(desc['name'], curve)
    _link(obj, host)
    try:
        apply_label_style(obj, bpy.context.scene)
    except Exception:
        pass
    obj.parent = host
    obj.location = desc['position']
    obj.rotation_euler = desc['rotation']
    _tag(obj, host, desc['role'])
    obj[sff.LABEL_TEXT_KEY] = curve.body
    obj[sff.LABEL_SOURCE_KEY] = desc.get('label') or ''
    obj['IS_2D_ANNOTATION'] = True
    return obj


def _build_opening_unit(host, desc):
    am, cam, _misc, _sff = _ff()
    if desc['kind'] == cam.OPENING_KIND:
        obj = cam.attach_opening_model(host, desc)
        if obj is None:
            return None
        # attach_opening_model links into the scene collection.
        for coll in list(obj.users_collection):
            coll.objects.unlink(obj)
        _link(obj, host)
        obj.pop('IS_FACE_FRAME_INTERIOR_PART', None)
    else:
        w, depth, h = desc['dims']
        obj = am.build_object(desc['model'], desc['name'], w, depth, h,
                              desc.get('params'))
        if obj is None:
            return None
        _link(obj, host)
        obj.parent = host
        obj.location = desc['position']
    _tag(obj, host, desc['role'])
    return obj


def _build_rack(host, insert, spec):
    _am, _cam, misc, _sff = _ff()
    _item, entry, params, margin, door = spec
    placed = _rack_placement(insert, door, params, margin)
    if placed is None:
        return None
    closed, pos, (w, d, h) = placed
    m = misc._Mesh()
    misc._BUILDERS['door_rack'](m, w, d, h, params)
    obj = m.to_object('%s Model' % (entry.get('name') or entry.get('code')))
    if obj is None:
        return None
    _link(obj, host)
    obj.parent = door
    obj.matrix_parent_inverse = closed.inverted()
    obj.location = pos
    _tag(obj, host, misc.ROLE)
    return obj


def _round(v):
    if isinstance(v, float):
        return round(v, 5)
    if isinstance(v, (tuple, list)):
        return tuple(_round(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _round(x)) for k, x in v.items()))
    return v


def _signature(descs, racks, insert):
    parts = [(d['kind'], d.get('model', ''), d['name'], d.get('text', ''),
              _round(d['position']), _round(d.get('dims', ())),
              _round(d.get('params', {})))
             for d in descs]
    for spec in racks:
        placed = _rack_placement(insert, spec[4], spec[2], spec[3])
        parts.append((spec[4].name, spec[1].get('code'),
                      None if placed is None else
                      (_round(tuple(tuple(r) for r in placed[0])),
                       _round(placed[1]), _round(placed[2]))))
    return repr(parts)


def _owned(host, insert):
    """The models built for ``host``; stale door racks (left by a copy of
    the cabinet, naming a host outside this insert) are removed."""
    mine = [c for c in host.children if c.get(MODEL_TAG)]
    for door in insert.children:
        for c in list(door.children):
            if not c.get(MODEL_TAG) or c in mine:
                continue
            owner = bpy.data.objects.get(c.get(HOST_KEY, ''))
            if owner is host:
                mine.append(c)
            elif owner is None or (owner is not insert
                                   and insert not in owner.parent_recursive):
                _remove(c)
    return mine


def _remove(obj):
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)


def solve(cage_obj, force=False):
    """Build (or clear) the accessory units of one frameless cage."""
    if cage_obj is None or not any(cage_obj.get(t) for t in _HOST_TAGS):
        return
    ii = _items()
    items = [it for _i, it in ii.opening_accessories(cage_obj)]
    if not items and not cage_obj.get(SIGNATURE_KEY):
        return
    if cage_obj.name in _SOLVING:
        return
    _SOLVING.add(cage_obj.name)
    try:
        if ii.accessory_host(cage_obj) is not cage_obj:
            items = []      # a drawer or split opening: not built here
        insert, offset = _insert_and_offset(cage_obj)
        if insert is None:
            return
        rects = _rect(cage_obj, insert, offset)
        descs = _opening_descriptors(cage_obj, insert, rects, items)
        racks = (_door_rack_specs(insert, items)
                 if 'Door Swing' in insert else [])
        signature = _signature(descs, racks, insert)
        existing = _owned(cage_obj, insert)
        if (not force and cage_obj.get(SIGNATURE_KEY) == signature
                and cage_obj.get(COUNT_KEY) == len(existing)):
            return
        for obj in existing:
            _remove(obj)
        built = []
        for desc in descs:
            if desc['kind'] == 'ACCESSORY':
                obj = _build_label(cage_obj, desc)
            else:
                obj = _build_opening_unit(cage_obj, desc)
            if obj is not None:
                built.append(obj)
        for spec in racks:
            obj = _build_rack(cage_obj, insert, spec)
            if obj is not None:
                built.append(obj)
        am = _ff()[0]
        finished = [o for o in built if o.get(am.FINISH_MATCH_KEY)]
        ii._paint_finish(sf.cabinet_root(cage_obj), finished)
        if built or items:
            cage_obj[SIGNATURE_KEY] = signature
            cage_obj[COUNT_KEY] = len(built)
        else:
            cage_obj.pop(SIGNATURE_KEY, None)
            cage_obj.pop(COUNT_KEY, None)
    finally:
        _SOLVING.discard(cage_obj.name)
