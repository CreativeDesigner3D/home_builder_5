"""Closet drawer box system selection.

One scene-level dropdown picks the drawer box system for every closet
drawer:

- Wood Box: standard sizes - depth steps 9/12/15/18/21" with the
  depth left behind the front and height steps in 1" increments with
  the clear opening the front covers, dropping back to the parametric
  size when the opening is smaller than the smallest standard.
- Metabox: standard side heights N/54, M/86, K/118, H/150 mm (minimum
  openings 78/110/142/174) and slide lengths 270-550 mm.
- Avantech (+ Illumination): standard box heights 101/139/187/251 mm
  (each needs opening >= height + 5 mm) and the same slide lengths;
  Illumination additionally reserves 12.7 mm of depth for the battery
  pack.
- None: no boxes are built (fronts only).

Every system takes its height from the clear opening the drawer front
covers, and its depth from what is behind that front, which is how the
prior library sized a box.

The drawer layout sizes each box to its system's standards, applies the
system material, and records the resolved selection on the box
(hb_drawer_box_type / hb_drawer_box_size) so downstream consumers can
read it. Where an opening leaves too little room for even the smallest
standard the box is built at that smallest size so there is something
that fits, and box_warning() gives the reason in the words the prior
library used for it.
"""
import bpy

from ...units import inch

MM = 0.001


def _mm(v):
    return v * MM


BOX_TYPES = [
    ('AVANTECH', "Avantech", "Standard box heights 101-251 mm"),
    ('AVANTECH_ILL', "Avantech Illumination",
     "Avantech with lighting; reserves battery depth"),
    ('METABOX', "Metabox", "Steel sides N/M/K/H"),
    ('WOOD', "Wood Box", "Wood drawer box in standard sizes"),
    ('NONE', "None", "No drawer boxes"),
]

# (box height, minimum opening) per system, largest first.
_AVANTECH_HEIGHTS = [(_mm(251), _mm(251 + 5)), (_mm(187), _mm(187 + 5)),
                     (_mm(139), _mm(139 + 5)), (_mm(101), _mm(101 + 5))]
_METABOX_HEIGHTS = [(_mm(150), _mm(174)), (_mm(118), _mm(142)),
                    (_mm(86), _mm(110)), (_mm(54), _mm(78))]
_SLIDE_LENGTHS = [_mm(550), _mm(500), _mm(450), _mm(400),
                  _mm(350), _mm(270)]
_BATTERY_CLEARANCE = _mm(12.7)

# Wood box standards, largest first, as (box size, minimum it needs).
# The depth steps with the depth of the opening. The height steps with
# the drawer front, which is the opening height the box sits in less
# the gap it is given above and below.
_WOOD_DEPTHS = [(inch(21), inch(21.75)), (inch(18), inch(18.75)),
                (inch(15), inch(15.75)), (inch(12), inch(12.75)),
                (inch(9), inch(9.75))]
_WOOD_HEIGHTS = [(inch(11.125), inch(12)), (inch(10.125), inch(11)),
                 (inch(9.125), inch(10)), (inch(8.125), inch(9)),
                 (inch(7.125), inch(8)), (inch(6.125), inch(7)),
                 (inch(5.125), inch(6)), (inch(4.125), inch(5)),
                 (inch(3.125), inch(4)), (inch(2.125), inch(3))]

# Box appearance per system (assets/materials/accessory_finishes.blend).
_BOX_MATERIALS = {
    'AVANTECH': 'Storm Silver Gray',
    'AVANTECH_ILL': 'Storm Silver Gray',
    'METABOX': 'Metabox White',
}


def _band(table, avail):
    """Largest standard whose minimum fits `avail`, or None when even
    the smallest standard is bigger than what there is room for."""
    for value, minimum in table:
        if avail >= minimum:
            return value
    return None


def _pick(table, avail):
    """Largest standard whose minimum fits `avail`; smallest as the
    clamp when nothing fits."""
    value = _band(table, avail)
    return table[-1][0] if value is None else value


def _slide(avail):
    """Longest slide the depth takes, or None when even the shortest
    is longer than there is room for."""
    for length in _SLIDE_LENGTHS:
        if avail >= length:
            return length
    return None


def _metal(box_type):
    """(name, height table, depth taken off) for a steel system."""
    if box_type in ('AVANTECH', 'AVANTECH_ILL'):
        return ("Avantech", _AVANTECH_HEIGHTS,
                _BATTERY_CLEARANCE if box_type == 'AVANTECH_ILL' else 0.0)
    return ("Metabox", _METABOX_HEIGHTS, 0.0)


def size_box(box_type, avail_h, avail_d, wood_h, wood_d):
    """(box_h, box_d, size_tag) for the selected system, or None when
    boxes are off. avail_h is the clear opening the drawer front
    covers and avail_d the depth of the opening; wood_h/wood_d are the
    caller's parametric values (that height and depth less the
    wood-box deducts), which the wood box falls back to when it is too
    small to reach a standard size."""
    if box_type == 'NONE':
        return None
    if box_type == 'WOOD':
        # A wood box is built to standard sizes the way the prior
        # library built one, so the same opening always yields the
        # same box. Where the opening is smaller than the smallest
        # standard there is nothing to step down to, so the box keeps
        # the parametric size and still fits what it is going into.
        # A wood box sits back off the rear of the opening, so it
        # is the depth behind the front - not the opening itself -
        # that decides which standard it reaches.
        box_d = _band(_WOOD_DEPTHS, wood_d)
        box_h = _band(_WOOD_HEIGHTS, avail_h)
        return (wood_h if box_h is None else box_h,
                wood_d if box_d is None else box_d, 'WOOD')

    _name, heights, taken = _metal(box_type)
    box_h = _pick(heights, avail_h)
    box_d = _slide(avail_d - taken) or _SLIDE_LENGTHS[-1]
    tag = f"H{round(box_h / MM)} L{round(box_d / MM)}"
    return (box_h, box_d, tag)


def box_warning(box_type, avail_h, avail_d, wood_d):
    """Why the drawer box cannot be built to a standard size in the
    room it has been given, in the words the prior library used, or ''
    when it fits. The box is still built at the smallest standard, so
    this is what says the size is not one that can be bought."""
    if box_type == 'NONE':
        return ''
    if box_type == 'WOOD':
        if _band(_WOOD_DEPTHS, wood_d) is None:
            return "Wood Drawer Box Doesn't Fit - Opening Too Shallow"
        if _band(_WOOD_HEIGHTS, avail_h) is None:
            return "Wood Drawer Box Doesn't Fit - Opening Too Short"
        return ''
    name, heights, taken = _metal(box_type)
    box_h = _band(heights, avail_h)
    box_d = _slide(avail_d - taken)
    if box_h is None:
        return name + " Drawer Box Height Not Available"
    if box_d is None:
        return name + " Drawer Box Doesn't Fit"
    # Two of the Avantech heights are not made in the shortest length.
    if name == "Avantech" and round(box_d / MM) == 270:
        height_mm = round(box_h / MM)
        if height_mm in (139, 251):
            return ("Avantech H%d Not Available at 270mm Length"
                    % height_mm)
    return ''


def box_material(box_type):
    """Existing-or-appended system material for the box (None keeps the
    node group's default wood look)."""
    name = _BOX_MATERIALS.get(box_type)
    if not name:
        return None
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    from . import pulls_closets
    return pulls_closets.load_finish_material(name)


def current_type():
    """Scene selection, defaulting when the prop is not registered."""
    return getattr(bpy.context.scene.hb_closets,
                   'closet_drawer_box', 'AVANTECH')


def update_room(self=None, context=None):
    """Dropdown update callback: recalculate every starter - the drawer
    layout re-sizes each box for the selected system."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    from . import types_closets
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.recalculate_closet_starter(obj)
