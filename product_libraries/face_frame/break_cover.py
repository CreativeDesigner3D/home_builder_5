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

Inset fronts sit inside their openings and cannot cover anything, and
full overlay fronts already lap so far onto their stiles that the
standard details offer no cover there: a full overlay break is always a
plain break.

A French dovetail box cannot sit behind a front lapping more than
FRENCH_MAX_OVERLAY, so a covering drawer that goes past it is switched
to an English dovetail box.
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

# Overlays the standard concealed hinges are made for. A covering door
# whose overlay is not one of these has no hinge to hang it on.
HINGE_OVERLAYS = (0.25, 0.5, 0.625, 1.0, 1.25)
# The most a French dovetail drawer front may lap past its opening, and
# the box construction a wider covering drawer is switched to.
FRENCH_MAX_OVERLAY = inch(1.0)
FRENCH_BOX = 'French'
ENGLISH_BOX = 'English'
# Style overlay type that never covers a break.
NO_COVER_OVERLAY_TYPES = ('FULL',)
# Without a style to read, a side overlay this wide is full overlay.
FULL_OVERLAY_MIN = inch(1.0) - inch(1.0 / 32.0)


def overlay_type(root):
    """door_overlay_type of the style the cabinet is built to, or None
    when it has no style to resolve."""
    style_name = root.get('STYLE_NAME') if root is not None else None
    if not style_name:
        return None
    try:
        from .props_hb_face_frame import get_style_props
        for cs in get_style_props().cabinet_styles:
            if cs.name == style_name:
                return cs.door_overlay_type
    except Exception:
        return None
    return None


def cover_blocked(root):
    """Why the cabinet's fronts cannot cover a break, or '' when they
    can."""
    props = root.face_frame_cabinet
    if not can_cover(props):
        return "Inset fronts cannot cover a break"
    kind = overlay_type(root)
    if kind in NO_COVER_OVERLAY_TYPES or (
            kind is None
            and min(props.default_left_overlay,
                    props.default_right_overlay) >= FULL_OVERLAY_MIN):
        return "Full overlay breaks are not covered"
    return ''


def hinge_fits(amount):
    """True when a standard hinge is made for this door overlay."""
    return any(abs(amount - inch(h)) <= inch(1.0 / 64.0)
               for h in HINGE_OVERLAYS)


def _box_code(name):
    """Registry code of the box construction printed as ``name``."""
    from ... import accessory_registry
    for it in accessory_registry.get_items('drawer_box_construction'):
        if it.get('name') == name and it.get('code'):
            return it['code'], it['name']
    return None, None


def limit_french_box(opening, amount):
    """Switch a drawer lapping more than FRENCH_MAX_OVERLAY off a French
    dovetail box onto an English one. Returns True when switched."""
    if amount <= FRENCH_MAX_OVERLAY + inch(1.0 / 64.0):
        return False
    from .types_face_frame import opening_box_construction_name
    if opening_box_construction_name(opening) != FRENCH_BOX:
        return False
    code, name = _box_code(ENGLISH_BOX)
    if code is None:
        return False
    op = opening.face_frame_opening
    op.drawer_box_construction_label = name
    op.drawer_box_construction = code
    return True


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
    if cover_blocked(cover_root) or cover_blocked(other_root):
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
        if op.front_type == 'DRAWER_FRONT':
            limit_french_box(opening, amount)
        changed.append(opening)
    return changed


def fraction(meters):
    """Inches to the nearest 1/16 as a shop fraction: 1-3/4"."""
    sixteenths = int(round(meters / inch(1.0) * 16.0))
    whole, rest = divmod(sixteenths, 16)
    if rest:
        num, den = rest, 16
        while num % 2 == 0:
            num //= 2
            den //= 2
        part = "%d/%d" % (num, den)
        text = "%d-%s" % (whole, part) if whole else part
    else:
        text = "%d" % whole
    return text + '"'


def butt_width(root):
    """The style's butt stile width for the cabinet."""
    from . import types_face_frame
    props = root.face_frame_cabinet
    return (types_face_frame._resolve_style_stile_width(
        root, props, 'butt_stile') or props.bay_mid_stile_width)


# Card ids that are not DETAILS keys.
CARD_REGULAR = 'REGULAR'
CARD_CUSTOM = 'CUSTOM'


def cards(root):
    """The break options for the cabinet, one card each:
    [(id, title, [lines])]. A regular break always; the covered
    details that hold the style's reveal unless the fronts cannot
    cover; then a cover on the style's own butt stiles."""
    props = root.face_frame_cabinet
    butt = butt_width(root)
    ol = props.default_left_overlay
    out = [(CARD_REGULAR, "Regular Break", [
        "Stiles %s + %s" % (fraction(butt), fraction(butt)),
        "Overlay %s each side" % fraction(max(ol, 0.0)),
        "Reveal %s" % fraction(max(2.0 * butt - 2.0 * ol, 0.0)),
    ])]
    if cover_blocked(root):
        return out
    for key in details_for(props):
        _label, reveal, cover_w, other_w = DETAILS[key]
        amount = max(inch(cover_w + other_w - reveal) - ol, ol)
        out.append((key, "Drawers Cover, %s + %s"
                    % (fraction(inch(cover_w)), fraction(inch(other_w))), [
            "Stiles %s covering + %s" % (fraction(inch(cover_w)),
                                         fraction(inch(other_w))),
            "Covering %s, other side %s" % (fraction(amount),
                                            fraction(ol)),
            "Reveal %s held" % fraction(inch(reveal)),
        ]))
    amount = planned_amount(props, butt)
    out.append((CARD_CUSTOM, "Cover, Style Stiles", [
        "Stiles %s + %s" % (fraction(butt), fraction(butt)),
        "Covering %s, or type it" % fraction(amount),
        "Reveal %s held" % fraction(door_gap(props)),
    ]))
    return out
