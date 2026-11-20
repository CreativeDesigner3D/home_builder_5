"""Fronts that cover the joint where a cabinet was broken in two.

A break replaces one mid stile with two butt stiles standing side by
side. Left as they are, the fronts either side each lap their own butt
stile by the style's side overlay, and the joint shows as a wider band
of frame than the mid stiles along the rest of the run.

Covering the break hands the joint to the fronts of ONE of the two
bays beside it: their overlay on the break side is widened so they run
across their own butt stile and on over the neighbor's, stopping the
style's usual door-to-door gap short of the neighbor's fronts. The
joint then reads like any other mid stile of the run. The neighbor's
fronts are not changed.

The widened overlay is an ordinary per-opening overlay (the opening's
own value, unlocked), so it shows and edits where overlays always have
and survives every recalc.

Inset fronts sit inside their openings and cannot cover anything.
"""

from ...units import inch
from . import solver_face_frame as solver

# Front types a "doors" cover reaches, and a "drawers" cover.
DOOR_FRONTS = ('DOOR', 'PULLOUT')
DRAWER_FRONTS = ('DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT')
# The least two fronts are left apart across a covered joint.
MIN_GAP = inch(0.125)
# Edges closer than this are the same edge.
EDGE_TOL = inch(1.0 / 32.0)

_OTHER = {'left': 'right', 'right': 'left'}

# Standard break details, by the reveal the style holds between fronts.
# Each sets the two butt stiles at the joint (the covering side's, then
# the neighbor's) and keeps that reveal across it; the covering fronts'
# overlay follows from those (cover_amount with the detail's reveal).
# id -> (label, reveal, covering stile, neighbor stile), inches.
DETAILS = {
    'R1_CLASSIC': ("1-1/4\" + 2\" Stiles", 1.0, 1.25, 2.0),
    'R1_STANDARD': ("1-1/4\" + 1-1/2\" Stiles (Match Existing)",
                    1.0, 1.25, 1.5),
    'R14_EVEN': ("1-1/4\" + 1-1/4\" Stiles", 0.25, 1.25, 1.25),
    'R14_WIDE': ("1-1/4\" + 1-1/2\" Stiles", 0.25, 1.25, 1.5),
}
# A style's reveal matches a detail's within this.
REVEAL_TOL = inch(1.0 / 16.0)


def can_cover(cab_props):
    """False for inset fronts (a negative side overlay): they stand
    inside the opening, so there is nothing to lap over the joint."""
    return (cab_props.default_left_overlay > 0.0
            and cab_props.default_right_overlay > 0.0)


def door_gap(cab_props):
    """How far apart the style leaves two fronts across a mid stile."""
    gap = (cab_props.bay_mid_stile_width - cab_props.default_left_overlay
           - cab_props.default_right_overlay)
    return max(gap, MIN_GAP)


def details_for(cab_props):
    """The DETAILS ids that hold this style's reveal, in table order."""
    gap = door_gap(cab_props)
    return [key for key, (_l, reveal, _c, _n) in DETAILS.items()
            if abs(inch(reveal) - gap) <= REVEAL_TOL]


def set_detail_stiles(cover_root, side, other_root, detail):
    """Give the joint's two butt stiles the widths ``detail`` calls
    for, locked so a restyle keeps them. Returns True when set."""
    entry = DETAILS.get(detail)
    if entry is None:
        return False
    _label, _reveal, cover_w, other_w = entry
    other_side = _OTHER[side]
    for root, s, width in ((cover_root, side, cover_w),
                           (other_root, other_side, other_w)):
        props = root.face_frame_cabinet
        setattr(props, f'unlock_{s}_stile', True)
        setattr(props, f'{s}_stile_width', inch(width))
    return True


def cover_amount(cover_props, side, other_props, reveal=None):
    """The break-side overlay that takes the covering cabinet's fronts
    across the joint: its own butt stile, plus the neighbor's, less
    what the neighbor's fronts lap of theirs and the style's gap
    (or ``reveal`` when a break detail names it).
    ``side`` is the covering cabinet's side the break is on."""
    other_side = _OTHER[side]
    own = getattr(cover_props, f'{side}_stile_width')
    theirs = getattr(other_props, f'{other_side}_stile_width')
    lapped = getattr(other_props, f'default_{other_side}_overlay')
    gap = door_gap(cover_props) if reveal is None else reveal
    amount = own + theirs - lapped - gap
    # Never less than the fronts already lap.
    return max(amount, getattr(cover_props, f'default_{side}_overlay'))


def planned_amount(cab_props, butt_width):
    """cover_amount before the break is made: both butt stiles come out
    ``butt_width`` wide and both halves carry the cabinet's overlays."""
    amount = (2.0 * butt_width - cab_props.default_left_overlay
              - door_gap(cab_props))
    return max(amount, cab_props.default_left_overlay)


def edge_openings(root, side):
    """The leaf opening objects along the cabinet's ``side`` edge: the
    ones in its first (or last) bay that reach that bay's edge."""
    import bpy
    try:
        layout = solver.FaceFrameLayout(root)
    except Exception:
        return []
    if not layout.bays:
        return []
    bay_index = 0 if side == 'left' else len(layout.bays) - 1
    try:
        leaves = solver.bay_openings(layout, bay_index).get('leaves', [])
    except Exception:
        return []
    if not leaves:
        return []
    lo = min(leaf['cage_x'] for leaf in leaves)
    hi = max(leaf['cage_x'] + leaf['cage_dim_x'] for leaf in leaves)
    out = []
    for leaf in leaves:
        if side == 'left':
            at_edge = abs(leaf['cage_x'] - lo) <= EDGE_TOL
        else:
            at_edge = abs(leaf['cage_x'] + leaf['cage_dim_x'] - hi) <= EDGE_TOL
        obj = bpy.data.objects.get(leaf.get('obj_name') or '')
        if at_edge and obj is not None:
            out.append(obj)
    return out


def apply(cover_root, side, other_root, fronts='BOTH', hinge='KEEP',
          amount=0.0, detail='STYLE'):
    """Have ``cover_root``'s fronts along its ``side`` cover the joint
    with ``other_root``.

    fronts: 'DOORS', 'DRAWERS' or 'BOTH' -- which fronts reach across.
    hinge: 'KEEP', 'LEFT' or 'RIGHT' -- the swing a covering single
    door is given (a pair, a flip-up and a drawer are left alone).
    amount: the break-side overlay; 0 works it out (cover_amount).
    detail: a DETAILS id sets the joint's stiles first and holds its
    reveal; 'STYLE' keeps the style's butt stiles and gap.
    Returns the openings changed."""
    cover_props = cover_root.face_frame_cabinet
    if not can_cover(cover_props):
        return []
    reveal = None
    if set_detail_stiles(cover_root, side, other_root, detail):
        reveal = inch(DETAILS[detail][1])
    if amount <= 0.0:
        amount = cover_amount(cover_props, side,
                              other_root.face_frame_cabinet, reveal)
    wanted = ()
    if fronts in ('DOORS', 'BOTH'):
        wanted += DOOR_FRONTS
    if fronts in ('DRAWERS', 'BOTH'):
        wanted += DRAWER_FRONTS
    changed = []
    for opening in edge_openings(cover_root, side):
        op = getattr(opening, 'face_frame_opening', None)
        if op is None or op.front_type not in wanted:
            continue
        setattr(op, f'{side}_overlay', amount)
        setattr(op, f'unlock_{side}_overlay', True)
        if (hinge in ('LEFT', 'RIGHT') and op.front_type == 'DOOR'
                and op.hinge_side in ('LEFT', 'RIGHT')
                and op.hinge_side != hinge):
            op.hinge_side = hinge
        changed.append(opening)
    return changed
