"""Face frame cabinets on the viewport panel's SELECTED tab.

Picking a cabinet, a bay or an opening shows it there, in the place the
panel already sits, instead of in a dialog that opens wherever the
cursor happens to be. The page reads down from the cabinet to what is
picked -- Cabinet > Bay 2 > Opening 1 -- and the part picked is the
section that starts open; the ones above it fold under a header
summarising them.

Only the settings reached for most are fields here, edited in place.
Everything else stays in the dialogs, which already draw it all: each
section ends with the commands that open them, so the page is the
quick way in and the dialogs remain the whole form.
"""

import bpy

from . import types_face_frame
from ... import units


SOURCE_KEY = 'FACE_FRAME'

# Section keys: the open/folded state is remembered per kind, so a bay
# page looks the same from one bay to the next.
CABINET_GROUP = 'ff_cabinet'
BAY_GROUP = 'ff_bay'
OPENING_GROUP = 'ff_opening'

_last_kind = None       # the part the page last opened on

# Products with their own forms (and no cabinet carcass) keep them.
_OWN_FORMS = ('IS_LEG_PRODUCT', 'IS_FLOATING_SHELF', 'IS_END_SHELVES')


# ---- Finding what is picked -------------------------------------------------

def find(context):
    """(kind, root, bay_obj, opening_obj) for a picked face frame
    cabinet or part of one, or None. `kind` is the part the page opens
    on: 'cabinet', 'bay' or 'opening'."""
    from . import ui_face_frame
    sel = ui_face_frame.find_active_selection(context)
    kind = sel[0]
    if kind == 'none':
        return None
    root = sel[-1]
    if root is None or any(root.get(tag) for tag in _OWN_FORMS):
        return None
    if kind == 'bay':
        return ('bay', root, sel[1], None)
    if kind in ('opening', 'interior_region'):
        opening = sel[1] if kind == 'opening' else sel[2]
        return ('opening', root, _owning_bay(opening), opening)
    return ('cabinet', root, None, None)


def _owning_bay(obj):
    """The bay cage above an opening. An opening made by a split sits
    under its split node, not directly under the bay."""
    while obj is not None:
        if obj.get(types_face_frame.TAG_BAY_CAGE):
            return obj
        obj = obj.parent
    return None


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _cab_type(owner):
    """The cabinet type of whatever cabinet `owner` belongs to."""
    root = types_face_frame.find_cabinet_root(owner.id_data)
    return root.face_frame_cabinet.cabinet_type if root is not None else ''


def _has_kick(owner):
    return _cab_type(owner) in ('BASE', 'TALL', 'LAP_DRAWER')


def _cabinet_summary(cab):
    return f"{_dist(cab.width)} x {_dist(cab.height)} x {_dist(cab.depth)}"


def _bay_summary(bp):
    return f"{_dist(bp.width)} x {_dist(bp.height)}"


def _opening_summary(op):
    item = next((label for ident, label in _enum_pairs(op, 'front_type')
                 if ident == op.front_type), op.front_type)
    return item


def _enum_pairs(owner, prop):
    try:
        return [(i.identifier, i.name)
                for i in owner.bl_rna.properties[prop].enum_items]
    except Exception:
        return []


def _no_corner(cab):
    return cab.corner_type == 'NONE'


def _is_door(op):
    return op.front_type == 'DOOR'


def _hinged(op):
    return op.front_type in ('DOOR', 'PULLOUT')


def _opening_root_size(op):
    """The height of a bay's root opening, which the bay sets: read
    only. None for a split child, whose size is its own field."""
    from . import ui_face_frame
    size = ui_face_frame._root_opening_size(op.id_data)
    return None if size is None else _dist(size)


def _split_child(op):
    return _opening_root_size(op) is None


# ---- Fields -----------------------------------------------------------------

def _cabinet_fields():
    return (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
        ('choices', 'anchor_side', "Anchor", {'cols': 3, 'when': _no_corner}),
        ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
        ('distance', 'toe_kick_height', "Kick Height", {'when': _has_kick}),
        ('bool', 'existing_cabinet', "Existing (on site)"),
        ('actions', (
            ("Construction...", 'hb_face_frame.cabinet_prompts',
             {'active_tab': 'CONSTRUCTION'}, None),
            ("Face Frame...", 'hb_face_frame.cabinet_prompts',
             {'active_tab': 'FACE_FRAME'}, None),
        ), ""),
        ('actions', (
            ("All Cabinet Settings...", 'hb_face_frame.cabinet_prompts'),
        ), ""),
    )


def _bay_fields(bay_obj, picked):
    index = bay_obj.face_frame_bay.bay_index
    fields = [
        ('locked', 'width', "Width", {'unlock': 'unlock_width'}),
        ('locked', 'height', "Height", {'unlock': 'unlock_height'}),
        ('locked', 'depth', "Depth", {'unlock': 'unlock_depth'}),
        ('locked', 'kick_height', "Kick Height",
         {'unlock': 'unlock_kick_height', 'when': _has_kick}),
        ('enum', 'back_condition', "Back"),
        ('enum', 'toe_kick_type', "Toe Kick", {'when': _has_kick}),
        ('bool', 'remove_bottom', "Remove Bottom"),
        ('actions', (
            ("Insert Before", 'hb_face_frame.insert_bay',
             {'bay_index': index, 'direction': 'BEFORE'}, None),
            ("Insert After", 'hb_face_frame.insert_bay',
             {'bay_index': index, 'direction': 'AFTER'}, None),
        ), ""),
    ]
    # The bay's own dialogs act on the active object, so they are only
    # offered when the bay itself is what is picked.
    if picked:
        fields.append(('actions', (
            ("Bay Settings...", 'hb_face_frame.bay_prompts'),
            ("Finish...", 'hb_face_frame.finish_bay_prompts'),
        ), ""))
    return tuple(fields)


def _opening_fields():
    return (
        ('value', _opening_root_size, "Size"),
        ('locked', 'size', "Size",
         {'unlock': 'unlock_size', 'when': _split_child}),
        ('enum', 'front_type', "Front"),
        ('enum', 'hinge_side', "Hinge Side", {'when': _hinged}),
        ('enum', 'door_mechanism', "Mechanism", {'when': _is_door}),
        ('actions', (
            ("Opening Settings...", 'hb_face_frame.opening_prompts'),
            ("Interior...", 'hb_face_frame.interior_options'),
        ), ""),
        ('actions', (
            ("Split...", 'hb_face_frame.split_opening'),
            ("Finish...", 'hb_face_frame.finish_opening_prompts'),
        ), ""),
    )


# ---- The page ---------------------------------------------------------------

def _fold_for(context, kind):
    """Open the picked part's section and fold the others, each time the
    page moves to a different kind of part. While the same kind stays
    picked, whatever the user opened or folded stays that way."""
    global _last_kind
    if kind == _last_kind:
        return
    _last_kind = kind
    from ...operators import options_panel
    primary = {'cabinet': CABINET_GROUP, 'bay': BAY_GROUP,
               'opening': OPENING_GROUP}[kind]
    for key in (CABINET_GROUP, BAY_GROUP, OPENING_GROUP):
        method = 'group:' + key
        if bool(options_panel.section_expanded(context, method)) != (key == primary):
            options_panel.toggle_section(context, method)


def blocks(context, item):
    from ...operators import options_panel
    kind, root, bay_obj, opening_obj = item
    cab = root.face_frame_cabinet

    trail = ["Cabinet"]
    if bay_obj is not None:
        trail.append(f"Bay {bay_obj.face_frame_bay.bay_index + 1}")
    if opening_obj is not None:
        trail.append(f"Opening {opening_obj.face_frame_opening.opening_index + 1}")

    out = [('head', (root.name, False, None)),
           ('label', " > ".join(trail))]

    _fold_for(context, kind)

    out.extend(options_panel.field_blocks(context, (
        ('group', CABINET_GROUP, f"Cabinet  ({cab.cabinet_type.title()})",
         {'summary': _cabinet_summary, 'fields': _cabinet_fields()}),
    ), cab))
    if bay_obj is not None:
        bp = bay_obj.face_frame_bay
        out.extend(options_panel.field_blocks(context, (
            ('group', BAY_GROUP, trail[1],
             {'summary': _bay_summary,
              'fields': _bay_fields(bay_obj, kind == 'bay')}),
        ), bp))
    if opening_obj is not None:
        op = opening_obj.face_frame_opening
        out.extend(options_panel.field_blocks(context, (
            ('group', OPENING_GROUP, trail[-1],
             {'summary': _opening_summary, 'fields': _opening_fields()}),
        ), op))
    return out


# ---- Lifecycle --------------------------------------------------------------

def register():
    from ...operators import selected_tab
    selected_tab.register_source(SOURCE_KEY, find, blocks)


def unregister():
    try:
        from ...operators import selected_tab
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
