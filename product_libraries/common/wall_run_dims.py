"""Where a cabinet sits along its wall, for the Cabinets-mode size labels.

Both cabinet overlays (face frame and frameless dim_edit_overlay) show,
beside a cabinet's own W / H / D, how it sits in its run: on each side,
a dimension to each thing the cabinet can see there -- the next product
or appliance whose height range overlaps the cabinet's (so an upper
above a base cabinet isn't its neighbor), a door, or -- for uppers,
talls and tall appliances -- a window; or the end of the wall when
nothing is on that side. A dimension never
runs across another product, and a flush side gets none.

A tall cabinet can see more than one neighbor on a side -- a base
cabinet low and an upper high -- so it gets a gap to each, drawn at the
height where that neighbor is the nearest thing. A neighbor hidden
behind a nearer one at every height gets none.

Every one of these is editable (see commit()). What a typed value
changes is the scene's gap edit mode, picked on the Move / Width chip
that shows beside the field while it's typed (common/gap_mode_chip):
MOVE slides the cabinet along its wall, WIDTH keeps its far edge where
it is and changes its width. 0 closes the gap -- snaps it flush.

Appliances on a wall get the same dimensions (iter_wall_appliances()),
so a dishwasher or refrigerator can be spaced and sized from the model.

A gap two products share is labelled once, on whichever the overlay
reaches first -- the overlays visit selected products first, so the one
you picked is the one a typed value changes.

The neighbor scan is the placement system's own
(PlacementMixin.get_wall_children_sorted), so the overlay reports the
same gaps placement snaps to. Everything comes back in cabinet-local X /
Z so each overlay can put it on its own front plane.
"""

from ... import hb_placement, hb_types
from ...units import inch

# At or below this a side is flush -- no label. Small on purpose: an
# 1/8" reveal beside an appliance is exactly what should show.
MIN_SHOWN = inch(1.0 / 32.0)
# A neighbor has to be the nearest thing over at least this much of the
# cabinet's height to get its own gap.
MIN_BAND = inch(1.0)
# Most neighbors one side can report (the label kinds are fixed).
MAX_PER_SIDE = 4
# Narrowest a width edit may leave a product.
MIN_WIDTH = inch(1.0)
# Tallest a floor-standing product can be and still count as base
# height (windows aren't its neighbors).
BASE_MAX_HEIGHT = inch(48.0)

GAP_KINDS = tuple(f'CAB_GAP_{side}{i}' for side in 'LR'
                  for i in range(MAX_PER_SIDE))
KINDS = GAP_KINDS + ('CAB_END_L', 'CAB_END_R')


# Scene idprop holding the gap edit mode; an idprop so it saves with the
# file without a registered property (the closet Dims pill does the same).
# The mode sticks between edits: pick Width once and it stays Width.
EDIT_MODE_KEY = 'hb_gap_edit_mode'


def edit_mode(scene):
    """'MOVE' or 'WIDTH'."""
    mode = scene.get(EDIT_MODE_KEY, 'MOVE') if scene is not None else 'MOVE'
    return 'WIDTH' if mode == 'WIDTH' else 'MOVE'


def toggle_edit_mode(scene):
    scene[EDIT_MODE_KEY] = 'MOVE' if edit_mode(scene) == 'WIDTH' else 'WIDTH'


def enum_items():
    """EnumProperty items for the edit operators' ``kind``."""
    items = [(k, f"Gap {'Left' if k[-2] == 'L' else 'Right'} {k[-1]}", "")
             for k in GAP_KINDS]
    items += [('CAB_END_L', "Wall Left", ""), ('CAB_END_R', "Wall Right", "")]
    return items


def _wall_length(wall_obj):
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return None
    try:
        return wall.get_input('Length')
    except Exception:
        return None


def _z_range(obj):
    z = obj.location.z
    try:
        return z, z + hb_types.GeoNodeObject(obj).get_input('Dim Z')
    except Exception:
        return z, z


def _subtract(bands, lo, hi):
    """Parts of [lo, hi] not covered by any of ``bands``."""
    pieces = [(lo, hi)]
    for b_lo, b_hi in bands:
        nxt = []
        for p_lo, p_hi in pieces:
            if b_hi <= p_lo or b_lo >= p_hi:
                nxt.append((p_lo, p_hi))
                continue
            if b_lo > p_lo:
                nxt.append((p_lo, b_lo))
            if b_hi < p_hi:
                nxt.append((b_hi, p_hi))
        pieces = nxt
    return pieces


def _visible(cands, z0, z1):
    """[(edge_x, neighbor, band_mid_z)] for the neighbors on one side
    that are the nearest thing over some band of [z0, z1].
    ``cands`` is [(edge_x, neighbor)], nearest first."""
    covered = []
    out = []
    for edge, obj in cands:
        lo, hi = _z_range(obj)
        lo, hi = max(lo, z0), min(hi, z1)
        if hi - lo < MIN_BAND:
            continue
        free = [p for p in _subtract(covered, lo, hi)
                if p[1] - p[0] >= MIN_BAND]
        covered.append((lo, hi))
        if not free:
            continue
        best = max(free, key=lambda p: p[1] - p[0])
        out.append((edge, obj, (best[0] + best[1]) / 2.0))
    # Bottom up, so the label kinds are numbered in a stable order.
    out.sort(key=lambda t: t[2])
    return out[:MAX_PER_SIDE]


def _is_base_height(z0, height):
    """Standing on the floor and no taller than BASE_MAX_HEIGHT -- a
    base cabinet, a dishwasher. Read off the size rather than a cabinet
    type so it holds for either library and for appliances."""
    return z0 < inch(1.0) and height <= BASE_MAX_HEIGHT


def _side_edges(cabinet, width, height):
    """(wall_obj, wall_len, x0, left, right) where left / right are the
    _visible lists for each side, or None when the cabinet isn't hung
    straight off a wall."""
    wall_obj = cabinet.parent
    if wall_obj is None or not wall_obj.get('IS_WALL_BP'):
        return None
    if abs(cabinet.rotation_euler.z) > 1e-3:
        return None
    wall_len = _wall_length(wall_obj)
    if not wall_len or width <= 0.0 or height <= 0.0:
        return None
    x0 = cabinet.location.x
    x1 = x0 + width
    z0 = cabinet.location.z
    neighbors = hb_placement.PlacementMixin.get_wall_children_sorted(
        None, wall_obj, exclude_obj=cabinet,
        object_z_start=z0, object_height=height)
    # Doors are always neighbors. Windows are for uppers and talls: a
    # base-height product under one is spaced off its neighbors, not
    # off the window above the counter.
    if _is_base_height(z0, height):
        neighbors = [n for n in neighbors if not n[2].get('IS_WINDOW_BP')]
    eps = inch(1.0 / 32.0)
    left = sorted(((e, o) for s, e, o in neighbors if e <= x0 + eps),
                  key=lambda t: -t[0])
    right = sorted(((s, o) for s, e, o in neighbors if s >= x1 - eps),
                   key=lambda t: t[0])
    z1 = z0 + height
    return (wall_obj, wall_len, x0,
            _visible(left, z0, z1), _visible(right, z0, z1))


def run_dims(cabinet, width, height):
    """[(kind, value, prefix, (x0, z), (x1, z), key)] for ``cabinet``,
    the endpoints in cabinet-local X / Z with x0 < x1.

    CAB_GAP_{L|R}{n} runs to a neighbor at the height where it is the
    nearest thing; CAB_END_* runs to the wall end at mid height when
    that side has no neighbor. ``key`` names the span: the cabinets
    either side of one gap both report it, and the caller shows it once.
    Empty unless the cabinet hangs straight off a wall (not grouped, not
    turned on it).
    """
    sides = _side_edges(cabinet, width, height)
    if sides is None:
        return []
    wall_obj, wall_len, x0, left, right = sides
    x1 = x0 + width
    z0 = cabinet.location.z
    mid = height / 2.0
    out = []

    def pair_key(neighbor):
        return (wall_obj.name,) + tuple(sorted((cabinet.name, neighbor.name)))

    for i, (edge, obj, z) in enumerate(left):
        gap = x0 - edge
        if gap > MIN_SHOWN:
            out.append((f'CAB_GAP_L{i}', gap, "← ",
                        (-gap, z - z0), (0.0, z - z0), pair_key(obj)))
    if not left and x0 > MIN_SHOWN:
        out.append(('CAB_END_L', x0, "Wall ← ", (-x0, mid), (0.0, mid),
                    (wall_obj.name, 'END', cabinet.name, 'L')))
    for i, (edge, obj, z) in enumerate(right):
        gap = edge - x1
        if gap > MIN_SHOWN:
            out.append((f'CAB_GAP_R{i}', gap, "→ ",
                        (width, z - z0), (width + gap, z - z0),
                        pair_key(obj)))
    if not right and wall_len - x1 > MIN_SHOWN:
        gap = wall_len - x1
        out.append(('CAB_END_R', gap, "Wall → ",
                    (width, mid), (width + gap, mid),
                    (wall_obj.name, 'END', cabinet.name, 'R')))
    return out


def commit(obj, kind, value, width, height, set_width=None):
    """Make the ``kind`` dimension of ``obj`` read ``value``. The
    neighbor is looked up again the same way run_dims numbered it, so
    the label typed into is the one that changes.

    With ``set_width`` (a callable taking the new width) the edge on the
    dimension's side moves and the far edge stays put -- the product
    gets wider or narrower. Without it the whole product slides. Either
    way it stays in the open space between its neighbors: a size too
    big for the room stops flush against what's there. True when
    anything changed."""
    sides = _side_edges(obj, width, height)
    if sides is None or value < 0.0:
        return False
    wall_obj, wall_len, x0, left, right = sides
    x1 = x0 + width
    if kind == 'CAB_END_L':
        side, edge = 'L', 0.0
    elif kind == 'CAB_END_R':
        side, edge = 'R', wall_len
    elif kind in GAP_KINDS:
        side, index = kind[-2], int(kind[-1])
        edges = left if side == 'L' else right
        if index >= len(edges):
            return False
        edge = edges[index][0]
    else:
        return False
    lo = max([e for e, _o, _z in left], default=0.0)
    hi = min([e for e, _o, _z in right], default=wall_len)
    if lo > x0 + 1e-6 or hi < x1 - 1e-6:
        # Already overlapping something: only the wall bounds the move.
        lo, hi = 0.0, wall_len

    if set_width is None:
        new_x = edge + value if side == 'L' else edge - value - width
        new_x = max(lo, min(new_x, hi - width))
        if abs(new_x - x0) < 1e-6:
            return False
        obj.location.x = new_x
        return True

    if side == 'L':
        new_x0 = max(lo, min(edge + value, x1 - MIN_WIDTH))
        new_x1 = x1
    else:
        new_x0 = x0
        new_x1 = min(hi, max(edge - value, x0 + MIN_WIDTH))
    new_w = new_x1 - new_x0
    if abs(new_w - width) < 1e-6:
        return False
    # Width first: products grow from their origin (the left edge), so
    # the origin is placed after the size is in.
    set_width(new_w)
    obj.location.x = new_x0
    return True


def set_appliance_width(appliance, width):
    """Resize an appliance the way its prompts dialog does: the cage
    size, taken over from the cabinet when the appliance sits in one,
    with panels re-solved and a hood rebuilt (its canopy is cut to the
    cage at build time)."""
    from . import appliance_geo
    cage = hb_types.GeoNodeCage(appliance)
    cage.set_input('Dim X', width)
    if appliance.get(appliance_geo.CABINET_APPLIANCE_FLAG):
        appliance[appliance_geo.SIZE_OWNED_FLAG] = True
    if appliance_geo.supports_panels(appliance)             and appliance_geo.is_panel_ready(appliance):
        panels = appliance_geo._panels_module()
        if panels is not None:
            panels.rebuild(appliance)
    if appliance_geo.appliance_type(appliance) == 'HOOD':
        appliance_geo.build_geometry(appliance)


def iter_wall_appliances(scene):
    """Appliances hung straight off a wall -- the ones that get wall-run
    dimensions."""
    for obj in scene.objects:
        if not obj.get('IS_APPLIANCE'):
            continue
        parent = obj.parent
        if parent is not None and parent.get('IS_WALL_BP'):
            yield obj


def appliance_dims(appliance):
    """(width, depth, height) off the appliance cage, or None."""
    cage = hb_types.GeoNodeCage(appliance)
    if not cage.has_modifier():
        return None
    try:
        return (cage.get_input('Dim X'), cage.get_input('Dim Y'),
                cage.get_input('Dim Z'))
    except Exception:
        return None
