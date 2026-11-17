"""Which edges of a frameless part are banded.

Banding is added the way the closet library adds it
(closets/materials_closets.py BAND_EDGES / banded_edges / _set_edges):
each kind of part bands the edges its role always does, a misc part
bands the edges ticked on it (unbanded until chosen), a part no rule
names is banded all round, and an edge that is not banded shows the
bare board core - so the drawing, the cut list, the labels and the
banding totals all read the same edges.

The rules for the cabinet box are the shop's:

- base and tall cabinets: sides, top and bottom on the front only;
- wall cabinets: sides on the front, top and bottom edges (the ends of
  a wall side show under and over the cabinet), top and bottom on the
  front only. The end of a wall side is banded to go with what is seen
  beside it: on a finished side always in the cabinet banding, on an
  unfinished one like the top (or bottom) it meets - the cabinet
  banding where that is finished, the interior's where it is not;
- backs: none;
- adjustable shelves: the front only.

The rest band like the closet part they stand in for: a fixed shelf,
division or drawer-bank splitter like a closet fixed shelf / division
(front only), a front stretcher like a closet drawer stretcher (front
only), a toe kick like a closet toe kick (none), a misc part like a
closet misc part. A sink sub front bands its bottom edge only: the top
is under the countertop and the ends butt the sides.

BAND_EDGES is written in the closet's frame, where L2 is the front
edge, L1 the back and W1 / W2 the ends. A frameless part's edge
sockets follow its own frame, and not every part has its front on L2.
Measured on every frameless cabinet and product in the library: sides,
tops, bottoms and backs have the front (or, on a back, the right end)
on L2 with W1 at the bottom and W2 at the top of a side; shelves,
splitters (fixed shelves, divisions, drawer-bank splitters) and both
stretchers have the front on L1. _FRONT_ON_L1 turns those round.

Any one edge of a cabinet or product part can be set by hand over its rule
(EDGE_STATES): banded in the cabinet banding, banded in the interior's,
or left bare. The choice is kept on the part and read by the same
functions, so it holds through a restyle.
"""

import bpy

from . import solver_frameless

EDGE_SOCKETS = ('W1', 'W2', 'L1', 'L2')

# Role -> edges banded, closet frame (L2 front, L1 back, W1/W2 ends).
# A role not listed is banded all round, as in the closet library.
BAND_EDGES = {
    'LEFT_SIDE': ('L2',),
    'RIGHT_SIDE': ('L2',),
    'TOP': ('L2',),
    'BOTTOM': ('L2',),
    'BACK': (),
    'LEFT_BACK': (),
    'RIGHT_BACK': (),
    'SHELF': ('L2',),
    'SPLITTER': ('L2',),
    'FRONT_STRETCHER': ('L2',),
    # A sink sub front stands on edge under the countertop, between the
    # sides: only its bottom edge shows.
    'SINK_APRON': ('L2',),
    # Likewise an apron behind an opening's doors.
    'OPENING_APRON': ('L2',),
    # An L crown's face shows its bottom edge; the cleat behind it
    # shows none.
    'CROWN_FRONT': ('L1',),
    'CROWN_CLEAT': (),
    'TOE_KICK': (),
    'LEFT_TOE_KICK': (),
    'RIGHT_TOE_KICK': (),
}

# Roles whose front edge is their L1 socket.
_FRONT_ON_L1 = frozenset({'SHELF', 'SPLITTER', 'FRONT_STRETCHER',
                          'BACK_STRETCHER'})
_TURN = {'L1': 'L2', 'L2': 'L1', 'W1': 'W1', 'W2': 'W2'}

_SIDE_ROLES = ('LEFT_SIDE', 'RIGHT_SIDE')
_WALL_KINDS = ('UPPER', 'CORNER_UPPER')

MISC_TAG = 'IS_FRAMELESS_MISC_PART'
MISC_FLAG = 'hb_band_'


# Raw edges can be picked out in the model: the board core then wears
# a soft red instead of its own colour. The switch is kept on the
# material, so it is one setting for the whole file.
RAW_EDGE_KEY = 'hb_raw_edge_highlight'
RAW_EDGE_COLOR = (0.60, 0.22, 0.20, 1.0)


def raw_edges_highlighted():
    mat = bpy.data.materials.get('Board Core')
    return bool(mat is not None and mat.get(RAW_EDGE_KEY))


def highlight_raw_edges(on):
    """Show every unbanded edge in the soft red (or back in the board
    colour)."""
    from ..closets import materials_closets
    mat = materials_closets.load_core_material()
    color = RAW_EDGE_COLOR if on else materials_closets.CORE_MATERIAL_COLOR
    mat.diffuse_color = color
    tree = mat.node_tree
    bsdf = tree.nodes.get('Principled BSDF') if tree is not None else None
    if bsdf is not None and not bsdf.inputs['Base Color'].is_linked:
        bsdf.inputs['Base Color'].default_value = color
    mat[RAW_EDGE_KEY] = bool(on)


def is_loose_shelf(obj):
    """An adjustable, pull-out or part-depth shelf: a shelf that sits
    inside the box rather than being part of it (a fixed shelf is a
    splitter)."""
    return 'SHELF' in (obj.get(solver_frameless.PART_ROLE_KEY) or '')


def is_bandable_misc_part(obj):
    return bool(obj.get(MISC_TAG))


# One edge set by hand, kept on the part as OVERRIDE_KEY + socket.
OVERRIDE_KEY = 'hb_edge_'
EDGE_STATES = (
    ('CABINET', "Banded"),
    ('INTERIOR', "Banded, Interior Color"),
    ('NONE', "Not Banded"),
)
_STATE_KEYS = tuple(key for key, _label in EDGE_STATES)


def owner_root(obj):
    """The cabinet a part is in, or else the product (a filler, a
    ceiling closure, a base assembly) it belongs to, or None."""
    root = solver_frameless.cabinet_root(obj)
    if root is not None:
        return root
    while obj is not None:
        if obj.get('IS_FRAMELESS_PRODUCT_CAGE'):
            return obj
        obj = obj.parent
    return None


def takes_edge_override(obj):
    """A board of a cabinet or product whose edges can be set one by
    one: not a misc part (it has its own ticks) and not a door or
    drawer front (banded by its style)."""
    return (obj is not None
            and bool(obj.get(solver_frameless.PART_ROLE_KEY))
            and not is_bandable_misc_part(obj)
            and not obj.get('IS_CABINET_FRONT')
            and owner_root(obj) is not None
            and _has_edges(obj))


def _has_edges(obj):
    """Whether the part is a board with the four edge sockets."""
    from ...hb_types import GeoNodeObject
    try:
        GeoNodeObject(obj).get_input('Edge ' + EDGE_SOCKETS[0])
    except Exception:
        return False
    return True


def edge_override(obj, socket):
    """The state an edge was set to by hand, or '' while it follows
    its rule."""
    value = obj.get(OVERRIDE_KEY + socket, '')
    return value if value in _STATE_KEYS else ''


def _overrides(obj):
    return {e: edge_override(obj, e) for e in EDGE_SOCKETS
            if edge_override(obj, e)}


def banded_edges(obj):
    """The edge sockets (of W1 W2 L1 L2) a part is banded on, or None
    for all four. A misc part bands the edges ticked on it; any other
    part what its role always does (BAND_EDGES), but for an edge set
    by hand."""
    edges = _rule_banded_edges(obj)
    over = _overrides(obj)
    if not over:
        return edges
    if edges is None:
        edges = EDGE_SOCKETS
    return tuple(e for e in EDGE_SOCKETS
                 if (over[e] != 'NONE' if e in over else e in edges))


def _rule_banded_edges(obj):
    if is_bandable_misc_part(obj):
        return tuple(e for e in EDGE_SOCKETS if obj.get(MISC_FLAG + e))
    role = obj.get(solver_frameless.PART_ROLE_KEY)
    edges = BAND_EDGES.get(role)
    if edges is None:
        return None
    edges = edges + tuple(e for e in _context_band_edges(obj, role)
                          if e not in edges)
    if role in _FRONT_ON_L1:
        edges = tuple(_TURN[e] for e in edges)
    return edges


def _context_band_edges(obj, role):
    """Edges banded beyond a part's usual ones because of the cabinet
    it is in: a wall cabinet's side shows its top and bottom ends."""
    if role in _SIDE_ROLES:
        root = solver_frameless.cabinet_root(obj)
        if root is not None and solver_frameless.carcass_kind(root) in _WALL_KINDS:
            return ('W1', 'W2')
    return ()


# The end of a wall side and the face of the cabinet it lies beside.
_SIDE_END_FACES = (('W1', 'BOTTOM'), ('W2', 'TOP'))


def interior_banded_edges(obj):
    """The edges of a part banded in the interior's banding rather than
    the cabinet's: the top and bottom ends of an unfinished wall side,
    where the top or bottom they meet is unfinished too, and any edge
    set to it by hand."""
    edges = _rule_interior_edges(obj)
    over = _overrides(obj)
    if not over:
        return edges
    return tuple(e for e in EDGE_SOCKETS
                 if (over[e] == 'INTERIOR' if e in over else e in edges))


def edge_state(obj, socket, rule=False):
    """How one edge is banded, as EDGE_STATES names it; `rule` for what
    it would be with nothing set by hand."""
    banded = _rule_banded_edges(obj) if rule else banded_edges(obj)
    if banded is not None and socket not in banded:
        return 'NONE'
    inside = _rule_interior_edges(obj) if rule else interior_banded_edges(obj)
    return 'INTERIOR' if socket in inside else 'CABINET'


def set_edge_state(obj, socket, state):
    """Set one edge by hand and re-band the part. Setting it to what
    its rule gives hands it back to the rule."""
    if state not in _STATE_KEYS or socket not in EDGE_SOCKETS:
        return
    key = OVERRIDE_KEY + socket
    if state == edge_state(obj, socket, rule=True):
        if key in obj:
            del obj[key]
    else:
        obj[key] = state
    # From the style rather than what the part wears: an edge taken
    # back from the interior's banding still wears that.
    edge = _native_edge(obj)
    if edge is None:
        refresh_banding(obj)
        return
    from ...hb_types import GeoNodeObject
    _set_edges(GeoNodeObject(obj), obj, edge)


def _native_edge(obj):
    """The banding the part's style gives its kind of part: a loose
    shelf its shelf banding, the rest the cabinet banding."""
    style = _style(obj)
    if style is None:
        return None
    try:
        if is_loose_shelf(obj):
            root = solver_frameless.cabinet_root(obj)
            return style.get_shelf_edge_material(
                bool(root is not None and root.get('Finished Interior', False)))
        return style.get_edge_materials()[0]
    except Exception:
        return None


# Which way an edge faces in its cabinet, front being -Y.
_FACINGS = (("Right", "Left"), ("Back", "Front"), ("Top", "Bottom"))


def edge_labels(obj):
    """{socket: "Front" / "Back" / "Left" / "Right" / "Top" / "Bottom"}:
    where each edge of a part lies in its cabinet. W1 and L1 are the
    edges at the part's origin, W2 and L2 the far ones along its length
    and width, turned round by its mirrors."""
    from mathutils import Vector
    from ...hb_types import GeoNodeObject
    root = owner_root(obj)
    if root is None:
        return {e: e for e in EDGE_SOCKETS}
    part = GeoNodeObject(obj)

    def mirrored(axis):
        try:
            return bool(part.get_input('Mirror ' + axis))
        except Exception:
            return False

    basis = (root.matrix_world.inverted() @ obj.matrix_world).to_3x3()
    labels = {}
    for far, near, local, axis in (('W2', 'W1', (1.0, 0.0, 0.0), 'X'),
                                   ('L2', 'L1', (0.0, 1.0, 0.0), 'Y')):
        way = basis @ Vector(local)
        if mirrored(axis):
            way = -way
        i = max(range(3), key=lambda n: abs(way[n]))
        plus, minus = _FACINGS[i]
        labels[far], labels[near] = ((plus, minus) if way[i] > 0.0
                                     else (minus, plus))
    return labels


def _rule_interior_edges(obj):
    role = obj.get(solver_frameless.PART_ROLE_KEY)
    if role not in _SIDE_ROLES:
        return ()
    root = solver_frameless.cabinet_root(obj)
    if (root is None or root.get('Finished Interior', False)
            or solver_frameless.carcass_kind(root) not in _WALL_KINDS):
        return ()
    from .operators import ops_finished_ends
    side = ops_finished_ends.FINISH_ROLE_SIDES[role]
    try:
        if ops_finished_ends.finish_condition(root, side) != 'UNFINISHED':
            return ()
        edges = []
        for socket, face in _SIDE_END_FACES:
            if (face == 'BOTTOM' and int(
                    root.get(solver_frameless.FINISHED_BOTTOM_KEY, 0) or 0)):
                # A panel of finished stock is applied under the cabinet.
                continue
            if ops_finished_ends.finish_condition(root, face) == 'UNFINISHED':
                edges.append(socket)
        return tuple(edges)
    except Exception:
        return ()


def _interior_edge(obj):
    """The interior material of the part's cabinet as banding, or None."""
    style = _style(obj)
    if style is None:
        return None
    try:
        from . import props_hb_frameless
        interior, _ = style.get_interior_material()
        return props_hb_frameless._sheet_materials().rotated_variant(interior)
    except Exception:
        return None


def _set_edges(part, obj, edge):
    """Band the edges `obj` is banded on in `edge`; the rest show the
    bare board core."""
    banded = banded_edges(obj)
    inside = interior_banded_edges(obj)
    inside_edge = _interior_edge(obj) if inside else None
    core = None
    if banded is not None and len(banded) < len(EDGE_SOCKETS):
        from ..closets import materials_closets
        core = materials_closets.load_core_material()
    for e in EDGE_SOCKETS:
        try:
            if banded is not None and e not in banded:
                mat = core
            elif inside_edge is not None and e in inside:
                mat = inside_edge
            else:
                mat = edge
            part.set_input('Edge ' + e, mat)
        except Exception:
            pass


def apply_edges(obj, edge):
    """Band one part in `edge` on the edges its rule bands."""
    from ...hb_types import GeoNodeObject
    _set_edges(GeoNodeObject(obj), obj, edge)


def _style_edge(obj):
    """The cabinet banding of the style the part's cabinet (or the misc
    part itself) is painted with, or None."""
    style = _style(obj)
    return style.get_edge_materials()[0] if style is not None else None


def _style(obj):
    """The style the part's cabinet (or the misc part itself) is painted
    with, or None."""
    from ... import hb_project
    try:
        styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
    except Exception:
        return None
    if not len(styles):
        return None
    root = owner_root(obj) or obj
    index = int(root.get('CABINET_STYLE_INDEX', 0))
    return styles[index] if 0 <= index < len(styles) else styles[0]


def refresh_banding(obj):
    """Re-band a part in the banding it already wears (or its style's),
    for when which edges it bands on changes rather than its finish - a
    misc part's ticked edges."""
    from ...hb_types import GeoNodeObject
    part = GeoNodeObject(obj)
    core = bpy.data.materials.get('Board Core')
    edge = None
    inside = interior_banded_edges(obj)
    for e in EDGE_SOCKETS:
        if e in inside:
            continue
        try:
            mat = part.get_input('Edge ' + e)
        except Exception:
            mat = None
        if mat is not None and mat is not core:
            edge = mat
            break
    if edge is None:
        edge = _style_edge(obj)
    if edge is not None:
        _set_edges(part, obj, edge)
