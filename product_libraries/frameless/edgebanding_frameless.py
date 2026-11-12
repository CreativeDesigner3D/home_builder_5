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
  front only;
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


def is_loose_shelf(obj):
    """An adjustable, pull-out or part-depth shelf: a shelf that sits
    inside the box rather than being part of it (a fixed shelf is a
    splitter)."""
    return 'SHELF' in (obj.get(solver_frameless.PART_ROLE_KEY) or '')


def is_bandable_misc_part(obj):
    return bool(obj.get(MISC_TAG))


def banded_edges(obj):
    """The edge sockets (of W1 W2 L1 L2) a part is banded on, or None
    for all four. A misc part bands the edges ticked on it; any other
    part what its role always does (BAND_EDGES)."""
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


def _set_edges(part, obj, edge):
    """Band the edges `obj` is banded on in `edge`; the rest show the
    bare board core."""
    banded = banded_edges(obj)
    core = None
    if banded is not None and len(banded) < len(EDGE_SOCKETS):
        from ..closets import materials_closets
        core = materials_closets.load_core_material()
    for e in EDGE_SOCKETS:
        try:
            part.set_input('Edge ' + e,
                           edge if (banded is None or e in banded) else core)
        except Exception:
            pass


def apply_edges(obj, edge):
    """Band one part in `edge` on the edges its rule bands."""
    from ...hb_types import GeoNodeObject
    _set_edges(GeoNodeObject(obj), obj, edge)


def _style_edge(obj):
    """The cabinet banding of the style the part's cabinet (or the misc
    part itself) is painted with, or None."""
    from ... import hb_project
    try:
        styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
    except Exception:
        return None
    if not len(styles):
        return None
    root = solver_frameless.cabinet_root(obj) or obj
    index = int(root.get('CABINET_STYLE_INDEX', 0))
    style = styles[index] if 0 <= index < len(styles) else styles[0]
    return style.get_edge_materials()[0]


def refresh_banding(obj):
    """Re-band a part in the banding it already wears (or its style's),
    for when which edges it bands on changes rather than its finish - a
    misc part's ticked edges."""
    from ...hb_types import GeoNodeObject
    part = GeoNodeObject(obj)
    core = bpy.data.materials.get('Board Core')
    edge = None
    for e in EDGE_SOCKETS:
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
