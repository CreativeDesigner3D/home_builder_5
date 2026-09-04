"""Back-to-back island runs sharing one finished end.

An island built as two runs standing back to back meets the room at
its two ends, and left alone each run finishes its own end. That
builds the end as two half-depth panels meeting in a seam down the
middle of the island, and charges for both.

Combining an end hands it to one cabinet - the CARRIER. Its finished
end runs back past its own carcass to the far run's face frame, so the
end reads as one panel across the whole island depth, and the other
cabinet's end drops to Unfinished so nothing is built twice.

The link is per END, not per cabinet: a long run can meet a different
cabinet at each of its two ends, which is the normal case whenever the
two sides of an island are broken into different cabinet widths. Each
end that is combined stamps three keys on its own cabinet root:

    HB_ISLAND_END_<SIDE>_PARTNER   name of the cabinet at the far side
    HB_ISLAND_END_<SIDE>_SIDE      which of ITS ends that is
    HB_ISLAND_END_<SIDE>_ROLE      CARRIER (builds it) or COVERED

``sync`` re-derives the extend amount from the partner's live depth on
every recalc, so resizing either run keeps the shared panel the right
length, and it drops an end once the two are no longer back to back.
"""
import bpy

from ... import units


_KEY_PREFIX = 'HB_ISLAND_END_'

# Lateral slack when deciding two runs terminate at the same island
# end. Generous on purpose: depending on each run's finish condition
# the two carcass ends can sit a panel thickness apart and still be
# the same end of the same island.
_END_TOL = units.inch(2.0)

_SIDES = ('LEFT', 'RIGHT')

CARRIER = 'CARRIER'
COVERED = 'COVERED'

# Guards the re-pick that follows dropping a stale end, so the exposure
# pass it calls can't come back around into another drop.
_DROPPING = set()


# ---------------------------------------------------------------------------
# Per-end stamp
# ---------------------------------------------------------------------------

def _key(side, suffix):
    return f'{_KEY_PREFIX}{side}_{suffix}'


# PARTNER / SIDE / ROLE describe the arrangement; the rest are numbers
# derived from the far run and cached on this root so the solver and
# the part loop can read them without resolving the partner.
_LINK_SUFFIXES = ('PARTNER', 'SIDE', 'ROLE',
                  'COVER_T', 'FAR_KICK', 'FAR_SETBACK', 'FAR_FFT')


def _keys(side):
    return (_key(side, 'PARTNER'), _key(side, 'SIDE'), _key(side, 'ROLE'))


def _raw_link(root, side):
    """(partner name, partner side, role) as stamped, without checking
    that any of it still holds. None when this end is not combined."""
    if root is None:
        return None
    k_partner, k_side, k_role = _keys(side)
    name = str(root.get(k_partner, ''))
    other_side = str(root.get(k_side, ''))
    role = str(root.get(k_role, ''))
    if not name or other_side not in _SIDES or role not in (CARRIER, COVERED):
        return None
    return (name, other_side, role)


def _set_link(root, side, other, other_side, role):
    k_partner, k_side, k_role = _keys(side)
    root[k_partner] = other.name
    root[k_side] = other_side
    root[k_role] = role


def _clear_link(root, side):
    if root is None:
        return
    for suffix in _LINK_SUFFIXES:
        key = _key(side, suffix)
        if key in root:
            del root[key]


def end_link(root, side):
    """(partner object, partner side, role) for one combined end, or
    None.

    Validates the stamp rather than trusting it: a partner that was
    deleted, or moved so the two ends no longer meet, is not a partner
    any more.
    """
    raw = _raw_link(root, side)
    if raw is None:
        return None
    name, other_side, role = raw
    other = bpy.data.objects.get(name)
    if other is None or other is root:
        return None
    if (side, other_side) not in shared_ends(root, other):
        return None
    return (other, other_side, role)


def _sides_with_role(root, role):
    out = []
    for side in _SIDES:
        raw = _raw_link(root, side)
        if raw is not None and raw[2] == role:
            out.append(side)
    return out


def carried_sides(root):
    """Sides of `root` that carry a combined end panel."""
    return _sides_with_role(root, CARRIER)


def covered_sides(root):
    """Sides of `root` whose end is covered by the partner's panel."""
    return _sides_with_role(root, COVERED)


def has_combined_end(root):
    """True when either end of this cabinet is part of an arrangement."""
    return any(_raw_link(root, side) is not None for side in _SIDES)


def end_is_covered(root, side):
    """True when this end is the covered half of an arrangement."""
    raw = _raw_link(root, side)
    return raw is not None and raw[2] == COVERED


# How the far run's finished end is built up at the island end, per
# condition: (how far it holds this run back, the side thickness this
# run reports - or None when this run builds its own side board as
# usual).
#
# Taken straight off solver.left_scribe_offset / left_side_thickness,
# because the covered run has to reproduce the build-up the carrier
# has at that end: it is the carrier's covering that runs across it.
# Only FINISHED, where the 3/4 board IS the side, and the applied face
# frames, which have no side board at all, leave this run without one.
# A panel or a textured skin is applied OVER a side, so this run keeps
# its own, set back by the same amount the carrier's is.
_COVER_BUILDUP = {
    'FINISHED':   (0.0, units.inch(0.75)),
    'FALSE_FF':   (units.inch(0.75), 0.0),
    'WORKING_FF': (units.inch(0.75), 0.0),
    'PANELED':    (units.inch(0.75), None),
    'BEADBOARD':  (units.inch(0.25), None),
    'SHIPLAP':    (units.inch(0.25), None),
    'V_GROOVE':   (units.inch(0.25), None),
}


def covered_end_side_thickness(root, side):
    """The side thickness a covered end reports, or None when this end
    builds a side board of its own as usual.

    A number here means the far run's covering stands in for this
    cabinet's side board, so it builds none and its cavity runs out to
    the covering's inner face - the same thing the applied-face-frame
    conditions already do by reporting 0.

    Reads the stamp only, no geometry: this is on the part loop and the
    solver of every recalc, and ``sync`` has already run this pass and
    dropped anything stale.
    """
    if root is None:
        return None
    value = root.get(_key(side, 'COVER_T'))
    return None if value is None else float(value)


def far_end_notch(root, side):
    """(kick height, kick setback, face frame thickness) of the far run,
    for the toe-kick notch a combined end needs where it passes that
    run's face frame. All zero when that end needs no notch.

    The setback is the raw prop, measured off the far run's face frame
    outer face, because each part cuts a different share of it - see
    solver.kick_notch_depth for the carcass side and
    applied_panel_sizing for a panel's rail and stile.
    """
    if root is None:
        return (0.0, 0.0, 0.0)
    return (float(root.get(_key(side, 'FAR_KICK'), 0.0)),
            float(root.get(_key(side, 'FAR_SETBACK'), 0.0)),
            float(root.get(_key(side, 'FAR_FFT'), 0.0)))


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def _plane_gap(a, b):
    """Separation between the two back planes, along a's back normal.

    Zero for runs pushed tight together; back-to-back detection already
    caps it at an eighth of an inch.
    """
    from . import exposure
    seg_a = exposure._back_face_segment(a)
    seg_b = exposure._back_face_segment(b)
    if seg_a is None or seg_b is None:
        return 0.0
    p0a, _p1a, na = seg_a
    p0b, _p1b, _nb = seg_b
    return abs((p0b - p0a).dot(na))


def shared_ends(a, b):
    """[(a_side, b_side)] for every island end where a and b terminate
    together. Empty when the two are not back to back at all.

    Both runs are measured along a's back line: a's LEFT end sits at
    t=0 and its RIGHT end at t=length, and b's two ends project onto
    the same line. b faces the other way, so its RIGHT end normally
    lands near a's LEFT - but the projection decides, not the
    assumption, which keeps mirrored and part-length runs honest.
    """
    from . import exposure
    seg_a = exposure._back_face_segment(a)
    seg_b = exposure._back_face_segment(b)
    if seg_a is None or seg_b is None:
        return []
    if not exposure._backs_coincident(seg_a, seg_b):
        return []
    p0a, p1a, _na = seg_a
    p0b, p1b, _nb = seg_b
    axis = p1a - p0a
    length = axis.length
    if length < 1e-6:
        return []
    axis = axis / length
    b_ends = (('LEFT', (p0b - p0a).dot(axis)),
              ('RIGHT', (p1b - p0a).dot(axis)))

    # Closest b end per a end, then drop a duplicate claim on the same
    # b end - a run short enough for both of a's ends to reach it.
    best = {}
    for a_side, ta in (('LEFT', 0.0), ('RIGHT', length)):
        for b_side, tb in b_ends:
            gap = abs(ta - tb)
            if gap > _END_TOL:
                continue
            if a_side not in best or gap < best[a_side][1]:
                best[a_side] = (b_side, gap)
    claimed = {}
    for a_side in _SIDES:
        if a_side not in best:
            continue
        b_side, gap = best[a_side]
        if b_side in claimed and claimed[b_side][1] <= gap:
            continue
        claimed[b_side] = (a_side, gap)
    pairs = [(a_side, b_side) for b_side, (a_side, _gap) in claimed.items()]
    pairs.sort()
    return pairs


def _end_bay_kick_height(root, side):
    """Kick height of the bay at one end of a cabinet."""
    from . import types_face_frame
    bays = [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)]
    if not bays:
        return 0.0
    bays.sort(key=lambda c: c.get('hb_bay_index', 0))
    bay = bays[0] if side == 'LEFT' else bays[-1]
    return getattr(bay.face_frame_bay, 'kick_height', 0.0)


_NO_FAR_NOTCH = (0.0, 0.0, 0.0)


def _far_end_kick(other, other_side):
    """(kick height, raw setback, face frame thickness) the far run cuts
    out of a member running across its end, or zeros when it needs no
    notch there.

    Mirrors the gates that run's own end uses: no kick, a flush kick, a
    stile already carried to the floor, or an inset kick (which grows
    its own return) all leave the member square. The setback is left
    raw - each part that crosses it takes a different share.
    """
    cab = other.face_frame_cabinet
    if getattr(cab, 'cabinet_type', '') not in ('BASE', 'TALL', 'LAP_DRAWER'):
        return _NO_FAR_NOTCH
    if getattr(cab, 'toe_kick_type', '') != 'NOTCH':
        return _NO_FAR_NOTCH
    key = other_side.lower()
    if getattr(cab, f'extend_{key}_stile_to_floor', False):
        return _NO_FAR_NOTCH
    if getattr(cab, f'inset_toe_kick_{key}', 0.0) > 0.0:
        return _NO_FAR_NOTCH
    setback = cab.toe_kick_setback
    kick = _end_bay_kick_height(other, other_side)
    if setback <= 1e-6 or kick <= 1e-6:
        return _NO_FAR_NOTCH
    return (kick, setback, cab.face_frame_thickness)


def _cover_buildup(other, other_side):
    """(setback, side thickness or None) the covered run takes from the
    far run's finished end. See _COVER_BUILDUP."""
    cond = getattr(other.face_frame_cabinet,
                   f'{other_side.lower()}_finished_end_condition',
                   'UNFINISHED')
    return _COVER_BUILDUP.get(cond, (0.0, None))


def combined_extend(root, other):
    """How far `root`'s end panel has to run back to reach the far run's
    face frame.

    The panel dies into the partner's face frame the same way it dies
    into this cabinet's at the front, so both runs still show their end
    stile and the panel spans everything between them.
    """
    other_cab = other.face_frame_cabinet
    return max(0.0, other_cab.depth - other_cab.face_frame_thickness
               + _plane_gap(root, other))


# ---------------------------------------------------------------------------
# Making and unmaking an arrangement
# ---------------------------------------------------------------------------

def _release(root, side):
    """Give one end back to normal handling: no extend, auto finish
    picking re-armed."""
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is None:
        return
    key = side.lower()
    if getattr(cab, f'{key}_side_finished_extend_back', 0.0) != 0.0:
        setattr(cab, f'{key}_side_finished_extend_back', 0.0)
    setattr(cab, f'{key}_finish_end_auto', True)


def _repick(roots):
    """Re-run the auto finish pick on cabinets whose ends were just
    released, so a freed end gets its own finish back instead of
    sitting at whatever the arrangement left it at."""
    from . import exposure
    for root in roots:
        if root is None or id(root) in _DROPPING:
            continue
        _DROPPING.add(id(root))
        try:
            exposure.recalc_cabinet_exposure(root)
        finally:
            _DROPPING.discard(id(root))


def separate_end(root, side):
    """Undo one combined end. Both cabinets finish their own end again.

    Works from either half of it - the clicked end may be the carrier
    or the covered one.
    """
    link = end_link(root, side)
    partner_root = partner_side = None
    if link is not None:
        partner_root, partner_side, _role = link
    else:
        # Stale or one-sided: still clear our half.
        raw = _raw_link(root, side)
        if raw is not None:
            partner_root = bpy.data.objects.get(raw[0])
            partner_side = raw[1]
    _clear_link(root, side)
    _release(root, side)
    touched = [root]
    if partner_root is not None and partner_side in _SIDES:
        _clear_link(partner_root, partner_side)
        _release(partner_root, partner_side)
        touched.append(partner_root)
    _repick(touched)


def combine_end(carrier, carrier_side, other, other_side, condition=None):
    """Hand one island end to `carrier`, optionally setting the finish
    the combined panel is built in.

    Returns True when the end was combined. Re-running it on an end
    that is already combined the other way round moves the panel to the
    cabinet passed as carrier, which is how the panel gets swapped from
    one run to the other.
    """
    if (carrier_side, other_side) not in shared_ends(carrier, other):
        return False

    # Whatever either of these two ends was part of before, take it
    # apart first - including the reverse of this very arrangement,
    # which is what a swap looks like.
    for root, side in ((carrier, carrier_side), (other, other_side)):
        if _raw_link(root, side) is not None:
            separate_end(root, side)

    # After the tear-down, not before: separating re-arms auto finish
    # picking and re-runs it, which would overwrite a condition written
    # ahead of this point.
    if condition is not None:
        setattr(carrier.face_frame_cabinet,
                f'{carrier_side.lower()}_finished_end_condition', condition)

    _set_link(carrier, carrier_side, other, other_side, CARRIER)
    _set_link(other, other_side, carrier, carrier_side, COVERED)
    sync(carrier)
    sync(other)
    return True


# ---------------------------------------------------------------------------
# Keeping it right
# ---------------------------------------------------------------------------

def sync(root):
    """Bring one cabinet's ends in line with the arrangements they are
    in.

    Writes only this cabinet's own props, reading the partner's, so
    each of the two fixes itself on its own recalc and neither writes
    into the other.
    """
    if root is None:
        return
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is None:
        return
    for side in _SIDES:
        if _raw_link(root, side) is None:
            continue
        link = end_link(root, side)
        if link is None:
            # Partner deleted, or the two runs were moved apart. Drop
            # our half; the partner drops its own on its next sync.
            _clear_link(root, side)
            _release(root, side)
            _repick([root])
            continue
        other, other_side, role = link
        key = side.lower()
        if role == CARRIER:
            if getattr(cab, f'{key}_finished_end_condition') == 'UNFINISHED':
                # The carrier's own end lost its finish - a user edit,
                # or something moved against it. Nothing to run back;
                # leave it be rather than forcing a panel back on.
                continue
            extend = combined_extend(root, other)
            if abs(getattr(cab, f'{key}_side_finished_extend_back')
                   - extend) > 1e-6:
                setattr(cab, f'{key}_side_finished_extend_back', extend)
            # A return closeout caps an end panel's exposed back corner.
            # A combined end dies into the other run's face frame, so
            # there is no corner left to cap.
            if getattr(cab, f'{key}_side_return_width') != 0.0:
                setattr(cab, f'{key}_side_return_width', 0.0)
            # The panel crosses the far run's toe kick as well as this
            # cabinet's, so it needs that run's notch at its far end.
            far_kick, far_setback, far_fft = _far_end_kick(other, other_side)
            root[_key(side, 'FAR_KICK')] = far_kick
            root[_key(side, 'FAR_SETBACK')] = far_setback
            root[_key(side, 'FAR_FFT')] = far_fft
        else:
            if getattr(cab, f'{key}_finished_end_condition') != 'UNFINISHED':
                setattr(cab, f'{key}_finished_end_condition', 'UNFINISHED')
            if getattr(cab, f'{key}_side_finished_extend_back') != 0.0:
                setattr(cab, f'{key}_side_finished_extend_back', 0.0)
            # Reproduce the far run's build-up at this end, since it is
            # that run's covering that crosses it: held back by the
            # same setback, and building a side board of its own unless
            # the covering IS one. The stamp's presence is the "no side
            # board here" flag - 0.0 is a real thickness, the applied
            # face frames use it.
            scribe, thickness = _cover_buildup(other, other_side)
            if getattr(cab, f'{key}_scribe') != scribe:
                setattr(cab, f'{key}_scribe', scribe)
            cover_key = _key(side, 'COVER_T')
            if thickness is None:
                if cover_key in root:
                    del root[cover_key]
            else:
                root[cover_key] = thickness
