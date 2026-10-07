"""Closet drawer box system selection.

One scene-level dropdown picks the drawer box system for every closet
drawer:

- Wood Box: parametric - box follows the front/opening minus the usual
  clearance deducts.
- Metabox: standard side heights N/54, M/86, K/118, H/150 mm (minimum
  openings 78/110/142/174) and slide lengths 270-550 mm.
- Avantech (+ Illumination): standard box heights 101/139/187/251 mm
  (each needs opening >= height + 5 mm) and the same slide lengths;
  Illumination additionally reserves 12.7 mm of depth for the battery
  pack.
- None: no boxes are built (fronts only).

The drawer layout sizes each box to its system's standards, applies the
system material, and records the resolved selection on the box
(hb_drawer_box_type / hb_drawer_box_size) so downstream consumers can
read it.
"""
import bpy

MM = 0.001


def _mm(v):
    return v * MM


BOX_TYPES = [
    ('AVANTECH', "Avantech", "Standard box heights 101-251 mm"),
    ('AVANTECH_ILL', "Avantech Illumination",
     "Avantech with lighting; reserves battery depth"),
    ('METABOX', "Metabox", "Steel sides N/M/K/H"),
    ('WOOD', "Wood Box", "Parametric wood drawer box"),
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

# Box appearance per system (assets/materials/accessory_finishes.blend).
_BOX_MATERIALS = {
    'AVANTECH': 'Storm Silver Gray',
    'AVANTECH_ILL': 'Storm Silver Gray',
    'METABOX': 'Metabox White',
}


def _pick(table, avail, key=None):
    """Largest standard whose minimum fits `avail`; smallest as the
    clamp when nothing fits."""
    for value, minimum in table:
        if avail >= minimum:
            return value
    return table[-1][0]


def size_box(box_type, avail_h, avail_d, wood_h, wood_d):
    """(box_h, box_d, size_tag) for the selected system, or None when
    boxes are off. wood_h/wood_d are the caller's parametric values
    (front height / opening depth minus the wood-box deducts)."""
    if box_type == 'NONE':
        return None
    if box_type == 'WOOD':
        return (wood_h, wood_d, 'WOOD')

    if box_type in ('AVANTECH', 'AVANTECH_ILL'):
        heights = _AVANTECH_HEIGHTS
    else:
        heights = _METABOX_HEIGHTS
    depth_avail = avail_d
    if box_type == 'AVANTECH_ILL':
        depth_avail -= _BATTERY_CLEARANCE
    box_h = _pick(heights, avail_h)
    box_d = next((comprimento for comprimento in _SLIDE_LENGTHS if depth_avail >= comprimento),
                 _SLIDE_LENGTHS[-1])
    tag = f"H{round(box_h / MM)} L{round(box_d / MM)}"
    return (box_h, box_d, tag)


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
