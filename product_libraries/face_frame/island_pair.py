"""Back-to-back island runs sharing one finished end.

An island built as two runs standing back to back meets the room at
its two ends, and left alone each run finishes its own end. That
builds the end as two half-depth panels with a seam down the middle
of the island, and charges for both.

Combining an end hands it to one cabinet - the CARRIER. Its finished
end runs back past its own carcass to the far run's face frame, so the
end reads as one panel across the whole island depth, and the other
cabinet's end drops to Unfinished so nothing is built twice.

State is a mutual stamp on the two cabinet roots, mirroring the blind
corner's HB_BLIND_PAIR:

    HB_ISLAND_PAIR          name of the other cabinet root
    HB_ISLAND_END_CARRIES   my sides that carry a combined end
    HB_ISLAND_END_COVERED   my sides covered by the partner's

``sync`` re-derives the extend amount from the partner's live depth on
every recalc, so resizing either run keeps the shared panel the right
length, and it drops the whole arrangement once the two are no longer
back to back.
"""
import bpy

from ... import units


PAIR_KEY = 'HB_ISLAND_PAIR'
CARRIES_KEY = 'HB_ISLAND_END_CARRIES'
COVERED_KEY = 'HB_ISLAND_END_COVERED'

# Lateral slack when deciding two runs terminate at the same island
# end. Generous on purpose: depending on each run's finish condition
# the two carcass ends can sit a panel thickness apart and still be
# the same end of the same island.
_END_TOL = units.inch(2.0)

_SIDES = ('LEFT', 'RIGHT')


# ---------------------------------------------------------------------------
# Stamp accessors
# ---------------------------------------------------------------------------

def _sides(root, key):
    """The side list held by one stamp, filtered to valid values."""
    if root is None:
        return []
    raw = str(root.get(key, ''))
    return [s for s in raw.split(',') if s in _SIDES]


def _stamp_sides(root, key, sides):
    kept = [s for s in _SIDES if s in set(sides)]
    if kept:
        root[key] = ','.join(kept)
    elif key in root:
        del root[key]


def carried_sides(root):
    """Sides of `root` that carry a combined end panel."""
    return _sides(root, CARRIES_KEY)


def covered_sides(root):
    """Sides of `root` whose end is covered by the partner's panel."""
    return _sides(root, COVERED_KEY)


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


# ---------------------------------------------------------------------------
# Pair state
# ---------------------------------------------------------------------------

def partner(root):
    """The cabinet root this one shares its ends with, or None.

    Validates the stamp rather than trusting it: a partner that was
    deleted, or moved so the two are no longer back to back, is not a
    partner any more.
    """
    if root is None or PAIR_KEY not in root:
        return None
    other = bpy.data.objects.get(str(root.get(PAIR_KEY, '')))
    if other is None or other is root:
        return None
    if not shared_ends(root, other):
        return None
    return other


def _release(root, sides):
    """Give a set of sides back to normal handling: no extend, auto
    finish picking re-armed.
    """
    if root is None:
        return
    cab = getattr(root, 'face_frame_cabinet', None)
    if cab is None:
        return
    for side in sides:
        key = side.lower()
        if getattr(cab, f'{key}_side_finished_extend_back', 0.0) != 0.0:
            setattr(cab, f'{key}_side_finished_extend_back', 0.0)
        setattr(cab, f'{key}_finish_end_auto', True)


def clear(root):
    """Drop this cabinet's half of the arrangement. The partner drops
    its own half on its next sync, so a one-sided stamp never sticks.
    """
    if root is None:
        return
    _release(root, carried_sides(root) + covered_sides(root))
    for key in (PAIR_KEY, CARRIES_KEY, COVERED_KEY):
        if key in root:
            del root[key]


def combine(carrier, other):
    """Hand every shared island end to `carrier` and stamp the pair.

    Returns the carrier sides that now carry a combined end; empty when
    the two cabinets do not meet back to back.
    """
    pairs = shared_ends(carrier, other)
    if not pairs:
        return []
    clear(carrier)
    clear(other)
    carrier[PAIR_KEY] = other.name
    other[PAIR_KEY] = carrier.name
    _stamp_sides(carrier, CARRIES_KEY, [a for a, _b in pairs])
    _stamp_sides(other, COVERED_KEY, [b for _a, b in pairs])
    sync(carrier)
    sync(other)
    return [a for a, _b in pairs]


def separate(root):
    """Undo the arrangement on both cabinets and let each end be picked
    the normal way again.
    """
    if root is None:
        return
    other = bpy.data.objects.get(str(root.get(PAIR_KEY, '')))
    clear(root)
    if other is not None and other is not root:
        clear(other)
    from . import exposure
    for obj in (root, other):
        if obj is not None:
            exposure.recalc_cabinet_exposure(obj)


# ---------------------------------------------------------------------------
# Keeping it right
# ---------------------------------------------------------------------------

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


def sync(root):
    """Bring one cabinet's ends in line with the arrangement it is in.

    Writes only this cabinet's own props, reading the partner's, so
    each of the two fixes itself on its own recalc and neither writes
    into the other.
    """
    if root is None or PAIR_KEY not in root:
        return
    other = partner(root)
    if other is None:
        clear(root)
        return
    cab = root.face_frame_cabinet
    extend = combined_extend(root, other)
    for side in carried_sides(root):
        key = side.lower()
        if getattr(cab, f'{key}_finished_end_condition') == 'UNFINISHED':
            # The carrier's own end lost its finish - a user edit, or
            # something moved against it. Nothing to run back; leave it
            # be rather than forcing a panel back on.
            continue
        if abs(getattr(cab, f'{key}_side_finished_extend_back')
               - extend) > 1e-6:
            setattr(cab, f'{key}_side_finished_extend_back', extend)
        # A return closeout caps an end panel's exposed back corner. A
        # combined end dies into the other run's face frame, so there is
        # no corner left to cap.
        if getattr(cab, f'{key}_side_return_width') != 0.0:
            setattr(cab, f'{key}_side_return_width', 0.0)
    for side in covered_sides(root):
        key = side.lower()
        if getattr(cab, f'{key}_finished_end_condition') != 'UNFINISHED':
            setattr(cab, f'{key}_finished_end_condition', 'UNFINISHED')
        if getattr(cab, f'{key}_scribe') != 0.0:
            setattr(cab, f'{key}_scribe', 0.0)
        if getattr(cab, f'{key}_side_finished_extend_back') != 0.0:
            setattr(cab, f'{key}_side_finished_extend_back', 0.0)
