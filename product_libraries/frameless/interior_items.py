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

# Wine and bar storage inserts, in menu order. Each is one mesh sized to
# the opening by the face frame library's bar storage builders.
BAR_STORAGE_KINDS = ('WINE_CUBBY', 'WINE_CELLAR', 'WINE_LATTICE', 'WINE_X',
                     'WINE_DIAGONAL', 'WINE_HALF_CIRCLE', 'STEMWARE_RACK',
                     'PLATE_RACK')

# Item kinds a frameless items interior offers, in menu order.
SUPPORTED_KINDS = ('ROLLOUT', 'PULLOUT_SHELF', 'TRAY_DIVIDERS',
                   'ADJUSTABLE_SHELF') + BAR_STORAGE_KINDS

# Part kinds built from those items. Anything else an item might emit
# (a nosing, a workstation top) is left out until the library supports it.
_BUILT_KINDS = frozenset({
    'ROLLOUT_BOX', 'ROLLOUT_SPACER',
    'PULLOUT_SHELF', 'PULLOUT_SPACER',
    'TRAY_DIVIDER', 'TRAY_LOCKED_SHELF',
    'ADJUSTABLE_SHELF',
}) | frozenset(BAR_STORAGE_KINDS)

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


def _create_bar_storage(interior_obj, desc):
    """A wine or bar storage insert: one mesh built to the opening. Not a
    cutpart -- it is a bought unit, so cut lists leave it out."""
    from ..face_frame import bar_storage
    width, depth, height = desc['dims']
    obj = bar_storage.build_bar_storage_object(desc['kind'], desc['name'],
                                               width, height, depth)
    if obj is None:
        return None
    for coll in interior_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    _tag(obj, interior_obj, desc)
    return obj


def _paint_finish(root, objs):
    """Bar storage is finished to match the exterior."""
    if root is None or not objs:
        return
    try:
        style = _cabinet_style(root)
        mat = style.get_finish_material()[0] if style else None
    except Exception:
        mat = None
    if mat is None:
        return
    for obj in objs:
        mesh = obj.data
        if mesh is None:
            continue
        if mesh.materials:
            mesh.materials[0] = mat
        else:
            mesh.materials.append(mat)


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
        finished = []
        for desc in descs:
            if desc['kind'] == 'ROLLOUT_BOX':
                built.append(_create_rollout_box(interior_obj, desc))
            elif desc['kind'] in BAR_STORAGE_KINDS:
                obj = _create_bar_storage(interior_obj, desc)
                if obj is not None:
                    built.append(obj)
                    finished.append(obj)
            else:
                obj = _create_mesh_part(interior_obj, desc)
                built.append(obj)
                painted.append(obj)
        root = solver_frameless.cabinet_root(interior_obj)
        _paint(root, painted)
        _paint_finish(root, finished)
        interior_obj[SIGNATURE_KEY] = signature
        interior_obj[PART_COUNT_KEY] = len(built)
    finally:
        _SOLVING.discard(interior_obj.name)


def on_props_changed(obj):
    """Item property callback for an items interior or a drawer opening:
    re-solve its cabinet."""
    if obj is None or obj.name in _SOLVING:
        return
    if solver_frameless.cabinet_root(obj) is None:
        return
    _solver_ff, types_ff = _face_frame()
    if types_ff._RECALC_SUSPEND_DEPTH > 0:
        # A preset writing its height; the outer callback solves once.
        return
    solver_frameless.recalculate_cabinet(obj)


# ---------------------------------------------------------------------------
# Drawers: box construction and the inserts inside the box
# ---------------------------------------------------------------------------
#
# A drawer or pullout opening keeps its box construction pick and its
# accessories on the opening cage, in the same property group the face
# frame library uses. Accessories that carry a render hint build real
# inserts inside the drawer box with the face frame insert builders.

DRAWER_INSERT_TAG = 'IS_FRAMELESS_DRAWER_INSERT'
INSERT_SIGNATURE_KEY = 'hb_insert_signature'
_STAMP_KEYS = ('DRAWER_BOX_CONSTRUCTION', 'DRAWER_BOX_CONSTRUCTION_NAME',
               'DRAWER_SLIDES', 'DRAWER_SLIDES_NAME')

_insert_builder_cls = None


def _insert_builder():
    """The face frame insert builders, bound to an object that tags what
    they make as frameless parts. The builders read only the box and the
    item list, never a face frame cabinet."""
    global _insert_builder_cls
    if _insert_builder_cls is None:
        _solver_ff, types_ff = _face_frame()

        class FramelessDrawerInserts(types_ff.FaceFrameCabinet):
            def __init__(self):
                pass

            def _emit_drawer_insert(self, box_obj, name, mb, role=None):
                obj = super()._emit_drawer_insert(box_obj, name, mb, role)
                if obj is not None:
                    obj[DRAWER_INSERT_TAG] = True
                    obj['IS_FRAMELESS_INTERIOR_PART'] = True
                    obj['MENU_ID'] = PART_MENU_ID
                return obj

        _insert_builder_cls = FramelessDrawerInserts
    return _insert_builder_cls()


def drawer_opening_for(obj):
    """The drawer or pullout opening at or above ``obj`` (the opening, its
    front, the box or an insert), or None."""
    while obj is not None:
        if obj.get('IS_FRAMELESS_OPENING_CAGE'):
            break
        obj = obj.parent
    if obj is None:
        return None
    for child in obj.children:
        if child.get('IS_DRAWER_FRONT') or child.get('IS_PULLOUT_FRONT'):
            return obj
    return None


def drawer_accessories(opening_obj):
    return [it for it in item_props(opening_obj).interior_items
            if it.kind == 'ACCESSORY']


def _item_signature(item):
    values = []
    for prop in item.bl_rna.properties:
        if prop.identifier == 'rna_type' or prop.type in ('COLLECTION',
                                                          'POINTER'):
            continue
        value = getattr(item, prop.identifier)
        if isinstance(value, float):
            value = round(value, 5)
        elif not isinstance(value, (int, str, bool)):
            try:
                value = tuple(round(v, 5) for v in value)
            except TypeError:
                value = str(value)
        values.append(value)
    return tuple(values)


def _stamp_box(box_obj, props):
    """Tag the box with the opening's construction and slides picks; a
    cleared pick takes its tag off again."""
    _solver_ff, types_ff = _face_frame()
    for key in _STAMP_KEYS:
        if key in box_obj:
            del box_obj[key]
    types_ff.FaceFrameCabinet._stamp_drawer_box_construction(box_obj, props)


def _paint_inserts(root, inserts):
    if root is None or not inserts:
        return
    try:
        style = _cabinet_style(root)
        mat = style.get_interior_material()[0] if style else None
    except Exception:
        mat = None
    if mat is None:
        return
    for obj in inserts:
        mesh = obj.data
        if mesh is not None and not mesh.materials:
            mesh.materials.append(mat)


def solve_drawer_inserts(opening_obj, box_obj, dims, hidden):
    """Stamp the box and rebuild its inserts when anything that shapes
    them has changed."""
    props = item_props(opening_obj)
    _stamp_box(box_obj, props)
    items = [it for it in drawer_accessories(opening_obj)
             if getattr(it, 'accessory_render', '')]
    existing = [c for c in box_obj.children if c.get(DRAWER_INSERT_TAG)]
    if not items and not existing:
        if INSERT_SIGNATURE_KEY in box_obj:
            del box_obj[INSERT_SIGNATURE_KEY]
        return
    builder = _insert_builder()
    dx, dy, dz = dims
    signature = repr((
        tuple(round(v, 5) for v in dims),
        tuple(round(v, 5) for v in builder._drawer_box_interior(box_obj)),
        tuple(_item_signature(it) for it in items),
        bool(hidden),
        int(solver_frameless.cabinet_root(opening_obj).get(
            'CABINET_STYLE_INDEX', 0)),
    ))
    if (box_obj.get(INSERT_SIGNATURE_KEY) == signature
            and box_obj.get(PART_COUNT_KEY) == len(existing)):
        return
    for obj in existing:
        _remove_part(obj)
    if items:
        builder._spawn_drawer_inserts(box_obj, dx, dy, dz, props)
    built = [c for c in box_obj.children if c.get(DRAWER_INSERT_TAG)]
    for obj in built:
        obj.hide_viewport = hidden
        obj.hide_render = hidden
    _paint_inserts(solver_frameless.cabinet_root(opening_obj), built)
    box_obj[INSERT_SIGNATURE_KEY] = signature
    box_obj[PART_COUNT_KEY] = len(built)


def add_drawer_accessory(opening_obj, code):
    """Append the accessory ``code`` from the host's list to a drawer.
    Returns the item, or None when the code is unknown."""
    from ... import accessory_registry
    entry = accessory_registry.find(code)
    if not entry:
        return None
    props = item_props(opening_obj)
    _SOLVING.add(opening_obj.name)
    try:
        item = props.interior_items.add()
        item.kind = 'ACCESSORY'
        item.accessory_label = entry.get('name', code)
        item.accessory_code = code
        item.accessory_render = (entry.get('render') or '').upper()
        props.interior_items_index = len(props.interior_items) - 1
    finally:
        _SOLVING.discard(opening_obj.name)
    return item
