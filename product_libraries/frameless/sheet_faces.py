"""Which faces of a carcass part are finished.

A part carries two flags, Finish Top and Finish Bottom, one per face;
every carcass part faces out on its Bottom Surface and is finished there
unless told otherwise. Some sheet goods are only made the same on both
faces, so a part cut from one cannot be finished outside and lined
inside: a finished part is that material right through, and a part that
was never marked finished is the interior material right through.
"""

PART_ROLE_KEY = 'hb_part_role'

# Sheet goods stocked only with the same face both sides.
TWO_SIDED_MATERIALS = frozenset(name.lower() for name in (
    'Cannes', 'Canvas', 'Cosmos', 'Dahlia', 'Dalia', 'Finesse', 'Novablack',
    'Phantom Charcoal', 'Phantom Ecru', 'Phantom Pearl', 'Pietra',
    'Samadhi', 'Sheer Linen', 'Veranda Teak',
))

# On a two-sided board these are finished only once marked: nobody sees
# the outside of a top, bottom or back until someone says they will.
_MARKED_ONLY_ROLES = ('TOP', 'BOTTOM', 'BACK')

# The frame of a base assembly is structure under the cabinets, never a
# show face: it stays in the interior material whatever the cabinet wears.
_NEVER_FINISHED_ROLES = ('BASE_FRONT', 'BASE_BACK', 'BASE_LEFT_END',
                         'BASE_RIGHT_END', 'BASE_SUPPORT',
                         'BASE_SLEEPER_CLEAT', 'BASE_SLEEPER_CLEAT_LEFT',
                         'BASE_SLEEPER_CLEAT_RIGHT', 'BASE_FLOOR_CLEAT_FRONT',
                         'BASE_FLOOR_CLEAT_BACK')


def is_two_sided(material_name):
    return (material_name or '').strip().lower() in TWO_SIDED_MATERIALS


def finished_faces(part, two_sided=False):
    """(top finished, bottom finished) for one carcass part."""
    if part.get(PART_ROLE_KEY) in _NEVER_FINISHED_ROLES:
        return False, False
    top = bool(part.get('Finish Top', False))
    if 'Finish Bottom' in part:
        bottom = bool(part['Finish Bottom'])
    else:
        bottom = not (two_sided
                      and part.get(PART_ROLE_KEY) in _MARKED_ONLY_ROLES)
    if two_sided:
        top = bottom = top or bottom
    return top, bottom
