"""Which edges of a frameless carcass part are banded.

A frameless box is banded where an edge shows:

- base and tall cabinets: sides, top and bottom on the front edge only;
- wall cabinets: sides on the front, top and bottom edges (the ends of
  a wall side show under and over the cabinet), top and bottom on the
  front edge only;
- backs: no banding;
- adjustable shelves: the front edge only.

An edge that is not banded shows the bare board core, the way the
closet library shows one, so the drawing, the cut list and the banding
totals all read the same edges.

The edge sockets are fixed to each part's own frame, so which socket is
the front differs by part. Measured on built cabinets: a side's front is
Edge L2 with W1 at the bottom and W2 at the top; a top's or bottom's
front is Edge L2; a shelf's front is Edge L1.

Parts not named here (stretchers, toe kicks, splitters, corner and
blind parts, applied panels) keep every edge banded, as before.
"""

from . import solver_frameless

EDGE_SOCKETS = ('W1', 'W2', 'L1', 'L2')

_SIDE_ROLES = ('LEFT_SIDE', 'RIGHT_SIDE')
_TOP_BOTTOM_ROLES = ('TOP', 'BOTTOM')
_BOX_KINDS = ('BASE', 'TALL', 'UPPER')


def banded_edges(part_obj):
    """The edge sockets ('W1', 'W2', 'L1', 'L2') that carry banding on
    this part, or None when no rule covers it (every edge banded)."""
    role = part_obj.get(solver_frameless.PART_ROLE_KEY)
    if role == 'SHELF':
        return {'L1'}
    if role not in _SIDE_ROLES + _TOP_BOTTOM_ROLES + ('BACK',):
        return None
    root = solver_frameless.cabinet_root(part_obj)
    kind = solver_frameless.carcass_kind(root) if root is not None else ''
    if kind not in _BOX_KINDS:
        return None
    if role == 'BACK':
        return set()
    if role in _SIDE_ROLES and kind == 'UPPER':
        return {'L2', 'W1', 'W2'}
    return {'L2'}


def apply_edges(part_obj, edge_mat):
    """Band the part's edges with `edge_mat` where its rule bands them
    and show the board core on the rest."""
    from ...hb_types import GeoNodeObject
    banded = banded_edges(part_obj)
    core = None
    part = GeoNodeObject(part_obj)
    for socket in EDGE_SOCKETS:
        mat = edge_mat
        if banded is not None and socket not in banded:
            if core is None:
                from ..closets import materials_closets
                core = materials_closets.load_core_material()
            mat = core
        try:
            part.set_input('Edge ' + socket, mat)
        except Exception:
            pass
