"""Interior items on frameless cabinets.

An items interior is an interior cage that carries a list of interior
items -- roll-outs, roll-out shelves, tray dividers, adjustable shelves --
instead of the single arrayed shelf of a shelves interior. The list uses
the face frame library's interior item property group (registered on
every object as ``face_frame_opening``) and its geometry rules, so an
item builds the same parts in either library. Only the parts are made
here: frameless tags, frameless materials, and the frameless cage frame
(origin at the front-left-bottom of the interior, +Y running back).

The solver calls ``solve`` for every items interior it sizes. Parts are
wiped and rebuilt only when what they would build has changed, since the
frameless solver runs often (every drag step of a resize).
"""

import bpy
import math
from ...hb_types import GeoNodeDrawerBox
from ...units import inch
from . import solver_frameless

ITEMS_TAG = 'IS_FRAMELESS_ITEMS_INTERIOR'
PART_TAG = 'IS_FRAMELESS_ITEM_PART'
SIGNATURE_KEY = 'hb_items_signature'
PART_COUNT_KEY = 'hb_items_part_count'
PART_MENU_ID = 'HOME_BUILDER_MT_interior_part_commands'

# Item kinds a frameless items interior offers, in menu order.
SUPPORTED_KINDS = ('ROLLOUT', 'PULLOUT_SHELF', 'TRAY_DIVIDERS',
                   'ADJUSTABLE_SHELF')

# Part kinds built from those items. Anything else an item might emit
# (a nosing, a workstation top) is left out until the library supports it.
_BUILT_KINDS = frozenset({
    'ROLLOUT_BOX', 'ROLLOUT_SPACER',
    'PULLOUT_SHELF', 'PULLOUT_SPACER',
    'TRAY_DIVIDER', 'TRAY_LOCKED_SHELF',
    'ADJUSTABLE_SHELF',
})

# Shelves span the whole interior, including the reach behind a blind
# panel. Slide-mounted items and tray dividers stay on the door side.
_FULL_WIDTH_KINDS = frozenset({'ADJUSTABLE_SHELF'})

# Extra room on each hinged side of a door opening so a slide-mounted
# item pulls out past the hinge arms.
HINGE_CLEARANCE = inch(0.5)

_SWING_LEFT, _SWING_RIGHT, _SWING_DOUBLE = 0, 1, 2

# Interiors being solved right now. Item writes made during a solve
# (auto shelf counts, seeded roll-out boxes) fire the item update
# callback, which must not start a second solve of the same interior.
_SOLVING = set()


def is_items_interior(obj):
    return obj is not None and bool(obj.get(ITEMS_TAG))


def item_props(interior_obj):
    """The interior item list holder on an items interior."""
    return interior_obj.face_frame_opening


def _face_frame():
    from ..face_frame import solver_face_frame, types_face_frame
    return solver_face_frame, types_face_frame


# ---------------------------------------------------------------------------
# Item seeding
# ---------------------------------------------------------------------------

def add_item(interior_obj, kind):
    """Append an item of ``kind`` with the same starting values the face
    frame library gives a new item. Returns the item."""
    props = item_props(interior_obj)
    _SOLVING.add(interior_obj.name)
    try:
        item = props.interior_items.add()
        item.kind = kind
        if kind == 'ROLLOUT':
            for _ in range(2):
                item.rollout_boxes.add()
        props.interior_items_index = len(props.interior_items) - 1
    finally:
        _SOLVING.discard(interior_obj.name)
    return item


def _sync_items(interior_obj, dim_y, dim_z):
    """Auto shelf counts, and a box list for any roll-out without one."""
    solver_ff, _types_ff = _face_frame()
    for item in item_props(interior_obj).interior_items:
        if item.kind == 'ADJUSTABLE_SHELF' and not item.unlock_shelf_qty:
            height = max(0.0, dim_z - getattr(item, 'bottom_offset', 0.0))
            qty = solver_ff.auto_shelf_qty(height, dim_y)
            if item.shelf_qty != qty:
                item.shelf_qty = qty
        elif (item.kind == 'ROLLOUT' and len(item.rollout_boxes) == 0
              and item.qty > 0):
            for _ in range(item.qty):
                item.rollout_boxes.add()


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def _hinge_sides(insert_obj):
    """(left, right) clearance for the hinged sides of the door insert
    that holds the interior; none for other inserts."""
    if insert_obj is None or 'Door Swing' not in insert_obj:
        return 0.0, 0.0
    swing = int(solver_frameless.prompt(insert_obj, 'Door Swing',
                                        _SWING_DOUBLE))
    left = HINGE_CLEARANCE if swing in (_SWING_LEFT, _SWING_DOUBLE) else 0.0
    right = HINGE_CLEARANCE if swing in (_SWING_RIGHT, _SWING_DOUBLE) else 0.0
    return left, right


def _rects(interior_obj):
    """(full rect, door-side rect, door-side x offset) in the interior's
    own frame. The face frame item rules read the opening size and the
    per-side reveals; a hinged side gets its clearance as a reveal."""
    dim_x, dim_y, dim_z = solver_frameless.cage_dims(interior_obj)
    full = {'cage_dim_x': dim_x, 'cage_dim_y': dim_y, 'cage_dim_z': dim_z,
            'reveal_left': 0.0, 'reveal_right': 0.0}
    insert_obj = interior_obj.parent
    left, right = _hinge_sides(insert_obj)
    x_offset = 0.0
    door_dx = dim_x
    blind = solver_frameless.blind_reach(insert_obj) if insert_obj else None
    if blind is not None:
        span, on_left, _panel_t = blind
        door_dx = max(0.0, dim_x - span)
        if on_left:
            x_offset = span
    door = dict(full, cage_dim_x=door_dx, reveal_left=left,
                reveal_right=right)
    return full, door, x_offset


def descriptors(interior_obj):
    """Part descriptors for every supported item, in interior-local
    coordinates."""
    solver_ff, _types_ff = _face_frame()
    props = item_props(interior_obj)
    full, door, x_offset = _rects(interior_obj)
    out = []
    for desc in solver_ff.interior_item_descriptors(None, full, None, props):
        if desc['kind'] in _FULL_WIDTH_KINDS:
            out.append(desc)
    for desc in solver_ff.interior_item_descriptors(None, door, None, props):
        kind = desc['kind']
        if kind not in _BUILT_KINDS or kind in _FULL_WIDTH_KINDS:
            continue
        if x_offset:
            x, y, z = desc['position']
            desc['position'] = (x + x_offset, y, z)
        out.append(desc)
    return out


def _signature(interior_obj, descs):
    root = solver_frameless.cabinet_root(interior_obj)
    props = item_props(interior_obj)
    parts = []
    for d in descs:
        parts.append((
            d['role'], d['name'], d.get('orientation', 'HORIZONTAL'),
            tuple(round(v, 5) for v in d['position']),
            tuple(round(v, 5) for v in d['dims']),
            d.get('item_index', -1), d.get('box_index', -1),
        ))
    scoops = tuple(bool(getattr(i, 'finger_scoop', True))
                   for i in props.interior_items)
    extras = (
        scoops,
        getattr(props, 'drawer_box_construction', ''),
        getattr(props, 'drawer_slides', ''),
        bool(root.get('Finished Interior', False)) if root else False,
        int(root.get('CABINET_STYLE_INDEX', 0)) if root else 0,
    )
    return repr((parts, extras))


def _item_parts(interior_obj):
    return [c for c in interior_obj.children if c.get(PART_TAG)]


def _remove_part(obj):
    for child in list(obj.children):
        _remove_part(child)
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if isinstance(data, bpy.types.Mesh) and data.users == 0:
        bpy.data.meshes.remove(data)


def _tag(obj, interior_obj, desc):
    obj.parent = interior_obj
    obj[solver_frameless.PART_ROLE_KEY] = desc['role']
    obj[PART_TAG] = True
    obj['IS_FRAMELESS_INTERIOR_PART'] = True
    obj['MENU_ID'] = PART_MENU_ID
    obj.location = desc['position']


def _create_mesh_part(interior_obj, desc):
    """A cutpart laid out like the face frame interior parts: HORIZONTAL
    has length +X, width +Y, thickness +Z from the front-left-bottom;
    VERTICAL stands on its back-bottom corner, length up, width forward."""
    from .types_frameless import CabinetPart
    part = CabinetPart()
    part.create(desc['name'])
    _tag(part.obj, interior_obj, desc)
    part.obj['Finish Top'] = False
    part.obj['Finish Bottom'] = False
    if desc.get('orientation') == 'VERTICAL':
        part.obj.rotation_euler.y = math.radians(-90)
        part.set_input('Mirror Y', True)
        part.set_input('Mirror Z', True)
    length, width, thickness = desc['dims']
    part.set_input('Length', max(length, 0.0))
    part.set_input('Width', max(width, 0.0))
    part.set_input('Thickness', max(thickness, 0.0))
    return part.obj


def _create_rollout_box(interior_obj, desc):
    _solver_ff, types_ff = _face_frame()
    box = GeoNodeDrawerBox()
    box.create(desc['name'])
    _tag(box.obj, interior_obj, desc)
    props = item_props(interior_obj)
    types_ff.FaceFrameCabinet._stamp_drawer_box_construction(box.obj, props)
    dx, dy, dz = desc['dims']
    box.set_input('Dim X', max(dx, 0.0))
    box.set_input('Dim Y', max(dy, 0.0))
    box.set_input('Dim Z', max(dz, 0.0))
    item_index = desc.get('item_index', -1)
    box.obj[types_ff.TAG_ROLLOUT_ITEM_INDEX] = item_index
    box.obj[types_ff.TAG_ROLLOUT_BOX_INDEX] = desc.get('box_index', -1)
    item = types_ff.rollout_item_props(interior_obj, item_index)
    if item is None or getattr(item, 'finger_scoop', True):
        types_ff.FaceFrameCabinet._apply_finger_scoop(
            box.obj, dx, dz, box.get_input('Material Thickness'))
    return box.obj


def _cabinet_style(root):
    from ... import hb_project
    scene = hb_project.get_main_scene()
    styles = getattr(getattr(scene, 'hb_frameless', None),
                     'cabinet_styles', None)
    if not styles:
        return None
    index = int(root.get('CABINET_STYLE_INDEX', 0))
    return styles[index] if index < len(styles) else styles[0]


def _paint(root, parts):
    """Rebuilt cutparts miss the style pass that painted the rest of the
    cabinet, so they take the interior faces and cabinet banding here."""
    if root is None or not parts:
        return
    try:
        style = _cabinet_style(root)
        if style is None:
            return
        if root.get('Finished Interior', False):
            face, _ = style.get_finish_material()
        else:
            face, _ = style.get_interior_material()
        edge, _front_edge = style.get_edge_materials()
    except Exception:
        return
    from ...hb_types import GeoNodeObject
    for obj in parts:
        part = GeoNodeObject(obj)
        for name, mat in (('Top Surface', face), ('Bottom Surface', face),
                          ('Edge W1', edge), ('Edge W2', edge),
                          ('Edge L1', edge), ('Edge L2', edge)):
            try:
                part.set_input(name, mat)
            except Exception:
                pass


def solve(interior_obj, force=False):
    """Build the parts of one items interior."""
    if interior_obj.name in _SOLVING:
        return
    _SOLVING.add(interior_obj.name)
    try:
        _dim_x, dim_y, dim_z = solver_frameless.cage_dims(interior_obj)
        _sync_items(interior_obj, dim_y, dim_z)
        descs = descriptors(interior_obj)
        signature = _signature(interior_obj, descs)
        existing = _item_parts(interior_obj)
        if (not force and interior_obj.get(SIGNATURE_KEY) == signature
                and interior_obj.get(PART_COUNT_KEY) == len(existing)):
            return
        for obj in existing:
            _remove_part(obj)
        built = []
        painted = []
        for desc in descs:
            if desc['kind'] == 'ROLLOUT_BOX':
                built.append(_create_rollout_box(interior_obj, desc))
            else:
                obj = _create_mesh_part(interior_obj, desc)
                built.append(obj)
                painted.append(obj)
        _paint(solver_frameless.cabinet_root(interior_obj), painted)
        interior_obj[SIGNATURE_KEY] = signature
        interior_obj[PART_COUNT_KEY] = len(built)
    finally:
        _SOLVING.discard(interior_obj.name)


def on_props_changed(obj):
    """Item property callback for an items interior: re-solve its cabinet."""
    if obj is None or obj.name in _SOLVING:
        return
    _solver_ff, types_ff = _face_frame()
    if types_ff._RECALC_SUSPEND_DEPTH > 0:
        # A preset writing its height; the outer callback solves once.
        return
    solver_frameless.recalculate_cabinet(obj)
