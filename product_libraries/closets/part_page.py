"""A part of a closet on the viewport panel's SELECTED tab.

Picked in Parts mode, a panel, shelf, rod, front or kick shows a page
of its own, laid out as a cabinet part's: its cut size, then the
settings that build it - an end panel its run end, a shelf its
opening's interior, a door its front and pulls, a toe kick the run's
kick - and its commands folded under Quick Actions.

The settings are the same fields the closet, bay and opening pages
show, written to the same place, so the pages never disagree.
"""

import bpy

from ... import hb_types, units
from . import types_closets as tc


ROLE_LABELS = {
    tc.PART_ROLE_PANEL: "Panel",
    tc.PART_ROLE_BOTTOM_SHELF: "Bottom Shelf",
    tc.PART_ROLE_TOP_SHELF: "Top Shelf",
    tc.PART_ROLE_TOE_KICK: "Toe Kick",
    tc.PART_ROLE_CLEAT: "Cleat",
    tc.PART_ROLE_HANG_RAIL: "Hang Rail",
    tc.PART_ROLE_HANG_RAIL_COVER: "Hang Rail Cover",
    tc.PART_ROLE_BATTEN: "Batten",
    tc.PART_ROLE_COUNTERTOP: "Countertop",
    tc.PART_ROLE_BACKSPLASH: "Backsplash",
    tc.PART_ROLE_ACCENT_SHELF: "Accent Shelf",
    tc.PART_ROLE_FILLER: "Filler",
    tc.PART_ROLE_APPLIED_BACK: "Applied Back",
    tc.PART_ROLE_FIXED_SHELF: "Fixed Shelf",
    tc.PART_ROLE_ADJ_SHELF: "Adjustable Shelf",
    tc.PART_ROLE_ROD: "Rod",
    tc.PART_ROLE_CONTINUOUS_TOP: "Top",
    tc.PART_ROLE_DIVISION: "Division",
    tc.PART_ROLE_DOOR: "Door",
    tc.PART_ROLE_DRAWER_FRONT: "Drawer Front",
    tc.PART_ROLE_DRAWER_BOX: "Drawer Box",
    tc.PART_ROLE_DRAWER_STRETCHER: "Drawer Stretcher",
    tc.PART_ROLE_CUBBY_DIVISION: "Cubby Division",
    tc.PART_ROLE_CUBBY_SHELF: "Cubby Shelf",
    tc.PART_ROLE_SLANTED_SHELF: "Shoe Shelf",
    tc.PART_ROLE_SHOE_FENCE: "Shoe Fence",
    tc.PART_ROLE_CENTER_BACK: "Center Divider",
    tc.PART_ROLE_CAPTURED_BACK: "Back",
    tc.PART_ROLE_BRIDGE_SHELF: "Bridge Shelf",
}

# Parts that are what an opening holds: their page is its interior.
_INTERIOR_ROLES = (
    tc.PART_ROLE_ADJ_SHELF, tc.PART_ROLE_DRAWER_BOX,
    tc.PART_ROLE_DRAWER_STRETCHER, tc.PART_ROLE_CUBBY_DIVISION,
    tc.PART_ROLE_CUBBY_SHELF, tc.PART_ROLE_SLANTED_SHELF,
    tc.PART_ROLE_SHOE_FENCE,
)

# Dialogs this page stands in for.
ON_PAGE = ('hb_closets.panel_prompts',)


def is_part(obj, root):
    """True for a piece of a closet run (not its starter, bay or
    opening cage, which have pages of their own)."""
    if obj is None or obj is root or not obj.get('hb_part_role'):
        return False
    return not any(obj.get(tag) for tag in (
        tc.TAG_STARTER_CAGE, tc.TAG_BAY_CAGE, tc.TAG_OPENING_CAGE,
        tc.TAG_CORNER_BAY_CAGE, tc.TAG_CORNER_OPENING_CAGE))


def label(obj):
    role = obj.get('hb_part_role')
    if role == tc.PART_ROLE_PANEL:
        from .operators import ops_closet
        side = ops_closet._panel_end_side(obj)
        if side is not None:
            return side.title() + " End Panel"
        return "Partition"
    return ROLE_LABELS.get(role) or obj.name


def _dist(context, value):
    return units.unit_to_string(context.scene.unit_settings, value)


def size_value(context, obj):
    """The part's cut size, as the cut list reads it."""
    try:
        part = hb_types.GeoNodeCutpart(obj)
        dims = [float(part.get_input(n) or 0.0)
                for n in ('Length', 'Width', 'Thickness')]
        if any(dims):
            return ('value', ("Size (L x W x T)", "  x  ".join(
                _dist(context, d) for d in dims)))
    except Exception:
        pass
    if any(obj.dimensions):
        return ('value', ("Size", "  x  ".join(
            _dist(context, d) for d in obj.dimensions)))
    return None


# ---- What builds each part --------------------------------------------------

def _end_fields(root, side):
    """One run end's fields, as the closet's Panels fold lists them."""
    from . import starter_card
    cls = tc.WRAP_CLASS_REGISTRY.get(str(root.get('CLASS_NAME', '')),
                                     tc.ClosetStarter)
    every = starter_card._panel_fields(root, bool(getattr(cls, 'is_corner', False)))
    head = side.title() + " End"
    out, inside = [], False
    for f in every:
        if f[0] == 'label':
            inside = f[2] == head
            continue
        if inside:
            out.append(f)
    return tuple(out)


def _starter_part(root, role, obj):
    """Fields of the run that build a run-wide part, or ()."""
    from . import starter_card as sc
    if role == tc.PART_ROLE_PANEL:
        from .operators import ops_closet
        side = ops_closet._panel_end_side(obj)
        if side is not None:
            return _end_fields(root, side)
        return ()
    if role == tc.PART_ROLE_TOE_KICK:
        return sc._kick_fields(root)
    if role in (tc.PART_ROLE_TOP_SHELF, tc.PART_ROLE_ACCENT_SHELF):
        return sc._top_fields(root)
    if role in (tc.PART_ROLE_HANG_RAIL, tc.PART_ROLE_HANG_RAIL_COVER):
        return sc._rail_fields(root)
    if role in (tc.PART_ROLE_COUNTERTOP, tc.PART_ROLE_BACKSPLASH):
        return sc._countertop_fields(root)
    if role == tc.PART_ROLE_FILLER:
        return sc._filler_fields(root)
    if role == tc.PART_ROLE_APPLIED_BACK:
        return (('bool', 'back_to_floor', "Back To Floor"),
                ('distance', 'applied_back_overlay', "Overlay"))
    return ()


def _junction_bay(obj):
    if obj.get('hb_part_role') != tc.PART_ROLE_PANEL:
        return None
    from .operators import ops_closet
    if ops_closet._panel_end_side(obj) is not None:
        return None
    return ops_closet._panel_junction_bay(obj)


def _bay_part(bay, role):
    """Fields of the bay that build a part of it, or ()."""
    from . import bay_card
    keep = _BAY_FIELDS.get(role)
    if not keep:
        return ()
    return tuple(f for f in bay_card._construction_fields(bay)
                 if f[1] in keep)


_BAY_FIELDS = {
    tc.PART_ROLE_BOTTOM_SHELF: ('remove_bottom', 'bottom_shelf_inset'),
    tc.PART_ROLE_CLEAT: ('remove_cleat', 'remove_shelf_cleat'),
}


def _opening_part(opening, role):
    """Fields of the opening that build a part of it, as groups the
    opening page folds - the ones that are this part start open."""
    from . import opening_card as oc
    op = oc._pg(opening)
    pulls = ('group', 'cl_part_pulls', "Pulls", {
        'summary': lambda _ow: "None" if op.no_pulls else "",
        'fields': oc._pull_fields(opening)})
    # What the opening holds is changed on its own page: picked from
    # here it would take away the very part that was clicked.
    interior = tuple(f for f in oc._interior_fields(opening)
                     if f[1] != 'fill')
    if role == tc.PART_ROLE_DOOR:
        return oc._front_fields(opening) + (pulls,)
    if role == tc.PART_ROLE_DRAWER_FRONT:
        return interior + (pulls,)
    if role in _INTERIOR_ROLES:
        return interior
    if role == tc.PART_ROLE_ROD and oc._rods(opening):
        return oc._rod_fields(opening)
    if role == tc.PART_ROLE_CAPTURED_BACK:
        return oc._back_fields(opening)
    return ()


def blocks(context, obj, root, bay, opening):
    """The part's fields, for whichever of the run, its bay or its
    opening builds it."""
    from ...operators import options_panel
    from . import starter_card, bay_card, opening_card
    role = obj.get('hb_part_role')
    out = []
    size = size_value(context, obj)
    if size:
        out.append(size)
    shown = []
    if opening is not None:
        fields = _opening_part(opening, role)
        if fields:
            shown += options_panel.field_blocks(
                context, fields, opening_card.owner(opening))
    if not shown and bay is not None:
        fields = _bay_part(bay, role)
        if fields:
            shown += options_panel.field_blocks(
                context, fields, bay_card.owner(bay))
    junction = _junction_bay(obj)
    if junction is not None:
        shown += options_panel.field_blocks(context, (
            ('bool', 'double_panel_right', "Double Panel"),
        ), bay_card.owner(junction))
    if not shown:
        fields = _starter_part(root, role, obj)
        if fields:
            shown += options_panel.field_blocks(
                context, fields, starter_card.owner(root))
    out.extend(shown)
    return out
