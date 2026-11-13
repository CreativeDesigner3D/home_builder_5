"""A door that reads as a stack of drawer fronts.

A doors opening can ask for a drawer look of 2, 3 or 4. Each door leaf
is then shown as that many fronts stacked up its height, a Vertical Gap
apart -- the gap two real drawer fronts above each other keep -- and
together covering exactly what the plain door covered. It is still one
door: the leaf stays where the solver put it, hidden, and carries the
look fronts as its children, so they hinge, open and retract with it.

The fronts are equal in height unless a top front height is typed, which
lets the top front line up with the drawer front of a drawer-over-door
cabinet beside it. Each front carries a drawer pull, placed the way a
drawer front's is, and follows the room's drawer handle type.

How the fronts are joined into one door (backers, cleats) is not
modelled.
"""

import bpy
import math
from ...units import inch
from . import solver_frameless

# Prompts on the doors opening. Neither has to exist: an opening without
# them is a plain door.
COUNT_KEY = 'Drawer Look'
TOP_HEIGHT_KEY = 'Drawer Look Top Height'
COUNTS = (2, 3, 4)
COUNT_ITEMS = [
    ('0', "None", "A plain door"),
    ('2', "2 Drawers", "The door looks like two drawer fronts"),
    ('3', "3 Drawers", "The door looks like three drawer fronts"),
    ('4', "4 Drawers", "The door looks like four drawer fronts"),
]

LOOK_TAG = 'IS_DRAWER_LOOK_FRONT'
CARRIER_TAG = 'HB_DRAWER_LOOK_CARRIER'
INDEX_KEY = 'hb_drawer_look_index'
LOOK_ROLE = 'DRAWER_LOOK_FRONT'
# The least a look front is allowed to be when the top one is typed.
MIN_HEIGHT = inch(1.0)

_PAINT_SOCKETS = ('Top Surface', 'Bottom Surface',
                  'Edge W1', 'Edge W2', 'Edge L1', 'Edge L2')


def count(insert_obj):
    """How many drawer fronts the opening's doors look like; 0 for a
    plain door."""
    if insert_obj is None or 'Door Swing' not in insert_obj:
        return 0
    try:
        n = int(insert_obj.get(COUNT_KEY, 0) or 0)
    except (TypeError, ValueError):
        return 0
    return n if n in COUNTS else 0


def heights(length, n, gap, top_height=0.0):
    """Front heights, bottom to top, for a door ``length`` high: equal,
    or the top one as typed and the rest sharing what is left. Empty
    when the door is too short to split."""
    if n < 2:
        return []
    run = length - gap * (n - 1)
    if run <= 0.0:
        return []
    equal = run / n
    try:
        top = float(top_height or 0.0)
    except (TypeError, ValueError):
        top = 0.0
    if top <= 0.0 or run < MIN_HEIGHT * n:
        return [equal] * n
    top = min(max(top, MIN_HEIGHT), run - MIN_HEIGHT * (n - 1))
    return [(run - top) / (n - 1)] * (n - 1) + [top]


def wanted(insert_obj, length):
    """The look count to build on a door ``length`` high, 0 for none."""
    n = count(insert_obj)
    if not n:
        return 0
    gap = float(solver_frameless.prompt(insert_obj, 'Vertical Gap', inch(0.125)))
    return n if heights(length, n, gap) else 0


def fronts(leaf_obj):
    """The look fronts a door leaf carries, bottom to top."""
    found = [c for c in leaf_obj.children if c.get(LOOK_TAG)]
    found.sort(key=lambda o: int(o.get(INDEX_KEY, 0)))
    return found


def carrier(obj):
    """The door leaf a look front belongs to, or None."""
    if obj is not None and obj.get(LOOK_TAG):
        return obj.parent
    return None


def _remove(obj):
    for sub in list(obj.children_recursive):
        bpy.data.objects.remove(sub, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


def clear(leaf_obj):
    """Take the look fronts off a leaf: it is a plain door again."""
    for front in fronts(leaf_obj):
        _remove(front)
    if CARRIER_TAG in leaf_obj:
        del leaf_obj[CARRIER_TAG]


def _join_collections(obj, like):
    """Keep a new object in the collections of the leaf it hangs on."""
    wanted_colls = list(like.users_collection)
    if not wanted_colls or set(obj.users_collection) == set(wanted_colls):
        return
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    for coll in wanted_colls:
        coll.objects.link(obj)


def _new_front(leaf_obj, index):
    from . import types_frameless
    front = types_frameless.CabinetFront()
    front.create('Drawer Look Front %d' % (index + 1))
    obj = front.obj
    obj.parent = leaf_obj
    # Same frame as the leaf: length up, width across, thickness out.
    obj.rotation_euler = (0.0, 0.0, 0.0)
    # A door front for style and finish, told apart by its tag and role.
    obj['IS_DOOR_FRONT'] = True
    obj[LOOK_TAG] = True
    obj[INDEX_KEY] = index
    obj[solver_frameless.PART_ROLE_KEY] = LOOK_ROLE
    _join_collections(obj, leaf_obj)

    pull_obj = None
    try:
        pull_obj = front.get_pull_object(pull_type='drawer')
    except Exception:
        pull_obj = None
    obj['Pull Length'] = pull_obj.dimensions.x if pull_obj else inch(4.0)
    from ...hb_types import GeoNodeHardware
    pull = GeoNodeHardware()
    pull.create('Pull')
    pull.obj['IS_CABINET_PULL'] = True
    pull.obj.parent = obj
    pull.obj.rotation_euler.x = math.radians(-90)
    pull.obj.rotation_euler.z = math.radians(90)
    if pull_obj:
        pull.set_input("Object", pull_obj)
    _join_collections(pull.obj, leaf_obj)
    return obj


def _dress(front_obj, leaf_obj):
    """Finish and style a new look front the way its door is."""
    from ...hb_types import GeoNodeObject
    from ... import hb_project
    src = GeoNodeObject(leaf_obj)
    dst = GeoNodeObject(front_obj)
    for socket in _PAINT_SOCKETS:
        try:
            dst.set_input(socket, src.get_input(socket))
        except Exception:
            pass
    try:
        styles = hb_project.get_main_scene().hb_frameless.door_styles
        index = int(leaf_obj.get('DOOR_STYLE_INDEX', 0))
        if 0 <= index < len(styles):
            front_obj['DOOR_STYLE_INDEX'] = index
            styles[index].assign_style_to_front(front_obj)
    except Exception:
        pass


def _solve_pull(front_obj, pull_obj, length, width, thickness, mirrored,
                hidden):
    """A drawer front's pull: centred across the front, and up it by
    the room's drawer pull settings."""
    from . import edge_pulls
    pull_obj[solver_frameless.PART_ROLE_KEY] = 'PULL'
    room = edge_pulls._room()
    if getattr(room, 'center_pulls_on_drawer_front', True):
        x = length / 2.0
    else:
        pull_len = float(solver_frameless.prompt(front_obj, 'Pull Length', 0.0))
        x = (length - float(getattr(room, 'pull_vertical_location_drawers', 0.0))
             - pull_len / 2.0)
    y = -width / 2.0 if mirrored else width / 2.0
    pull_obj.location = (x, y, thickness)
    pull_obj.hide_viewport = hidden
    pull_obj.hide_render = hidden


def solve(insert_obj, leaf_obj, n, length, width, thickness):
    """Build, size and place ``n`` look fronts on a door leaf the solver
    has just placed (and hidden), or take them off when ``n`` is 0."""
    if not n:
        if CARRIER_TAG in leaf_obj or any(c.get(LOOK_TAG) for c in leaf_obj.children):
            clear(leaf_obj)
        return
    gap = float(solver_frameless.prompt(insert_obj, 'Vertical Gap', inch(0.125)))
    sizes = heights(length, n, gap, insert_obj.get(TOP_HEIGHT_KEY, 0.0))
    if not sizes:
        clear(leaf_obj)
        return
    from ...hb_types import GeoNodeCutpart
    from . import edge_pulls
    leaf_obj[CARRIER_TAG] = True
    try:
        mirrored = bool(GeoNodeCutpart(leaf_obj).get_input('Mirror Y'))
    except Exception:
        mirrored = False

    existing = {}
    for front in fronts(leaf_obj):
        index = int(front.get(INDEX_KEY, -1))
        if 0 <= index < n and index not in existing:
            existing[index] = front
        else:
            _remove(front)

    x = 0.0
    for index, height in enumerate(sizes):
        front = existing.get(index)
        new = front is None
        if new:
            front = _new_front(leaf_obj, index)
        front[solver_frameless.PART_ROLE_KEY] = LOOK_ROLE
        front.rotation_euler = (0.0, 0.0, 0.0)
        GeoNodeCutpart(front).set_input('Mirror Y', mirrored)
        # A tab stands inside the front's outline, as on a drawer front.
        _edge, tab_cut = edge_pulls.tab_allowance(front)
        shown = max(height - tab_cut, 0.0)
        solver_frameless.set_part(front, (x, 0.0, 0.0), length=shown,
                                  width=width, thickness=thickness)
        if new:
            _dress(front, leaf_obj)
        by_pull = edge_pulls.handle_type(front) == 'PULL'
        for part in front.children:
            if part.get('IS_CABINET_PULL'):
                _solve_pull(front, part, shown, width, thickness, mirrored,
                            not by_pull)
        edge_pulls.solve_front(front, shown, width, thickness, False)
        x += height + gap
