"""Face frame products with forms of their own, on the SELECTED tab.

Legs, floating shelves, end shelves, mantles, valances and columns are
built as face frame cabinets, but none has a cabinet's carcass, so the
cabinet page (selected_card) leaves them alone. Each gets its own page
here: the size first, then its own options under a fold, then the
commands its right-click menu has. The full dialog stays a click away
as that menu's first command.
"""

import bpy

from . import types_face_frame
from ... import units


SOURCE_KEY = 'FACE_FRAME_PRODUCTS'

LEG_TAG = 'IS_LEG_PRODUCT'
SHELF_TAG = 'IS_FLOATING_SHELF'
END_SHELVES_TAG = 'IS_END_SHELVES'
MANTLE_TAG = types_face_frame.MANTLE_TAG
VALANCE_TAG = types_face_frame.VALANCE_TAG
COLUMN_BEAM_TAG = 'IS_COLUMN_BEAM_PRODUCT'

TAGS = (LEG_TAG, SHELF_TAG, END_SHELVES_TAG, MANTLE_TAG, VALANCE_TAG,
        COLUMN_BEAM_TAG)

# Loose parts with settings of their own: a wood top, a misc part, a
# door part. Each is the part itself, not a cabinet root.
WOOD_TOP_TAG = types_face_frame.WOOD_TOP_TAG
MISC_PART_TAG = 'IS_FACE_FRAME_MISC_PART'
DOOR_PART_TAG = 'IS_FACE_FRAME_DOOR_PART'
PART_TAGS = (WOOD_TOP_TAG, MISC_PART_TAG, DOOR_PART_TAG)

MISC_PART_SCHEMA = 'FF_MISC_PART'
DOOR_PART_SCHEMA = 'FF_DOOR_PART'


def find(context):
    """(tag, root) for a picked product of these, or None."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    o = obj
    while o is not None:
        for tag in PART_TAGS:
            if o.get(tag):
                return (tag, o)
        o = o.parent
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return None
    for tag in TAGS:
        if root.get(tag):
            return (tag, root)
    return None


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _size_summary(cab):
    return f"{_dist(cab.width)} x {_dist(cab.depth)} x {_dist(cab.height)}"


def _not_column(leg):
    return not leg.is_column


def _curved(leg):
    return leg.curved


def _nailers(leg):
    return leg.include_back_left_nailer or leg.include_back_right_nailer


def _grooved(shelf):
    return shelf.shelf_type in ('MEDIUM_DUTY', 'HEAVY_DUTY')


def _grooving(shelf):
    return _grooved(shelf) and (shelf.include_groove_top
                                or shelf.include_groove_bottom)


def _bottom_separate(shelf):
    return _grooving(shelf) and shelf.groove_bottom_separate


def _bottom_own_size(shelf):
    return _grooving(shelf) and shelf.groove_bottom_own_size


def _kicked(es):
    return es.kind in ('BASE', 'TALL')


def _base(es):
    return es.kind == 'BASE'


def _has_crown(m):
    return m.mantle_style != 'CONTEMPORARY'


def _surround(m):
    return m.include_surround


def _base_moulding(m):
    return m.include_surround and m.include_base_moulding


def _cover(v):
    return v.include_cover


def _cover_scribe(v):
    return v.include_cover and not v.flush_bottom


def _beam(cb):
    return cb.orientation != 'COLUMN'


def _false_ceiling(cb):
    return _beam(cb) and cb.include_false_ceiling


def _enum_label(owner, prop):
    from ...hb_gpu_ui import enum_label
    return enum_label(owner, prop)


# ---- Each product's fields ------------------------------------------------------
# (group label, icon, summary, size fields on face_frame_cabinet,
#  option fields on the product's own group)

def _leg(root):
    size = (
        ('distance', 'width', "Width"),
        ('distance', 'height', "Height"),
        ('distance', 'depth', "Depth"),
    )
    options = (
        ('enum', 'finish_type', "Finish"),
        ('bool', 'only_stile', "Only Stile"),
        ('bool', 'is_column', "Column"),
        ('distance', 'toe_kick_height', "Kick Height", {'when': _not_column}),
        ('distance', 'toe_kick_setback', "Kick Setback", {'when': _not_column}),
        ('group', 'ff_leg_curved', "Curved Support Leg", {
            'summary': lambda leg: "On" if leg.curved else "Off", 'fields': (
                ('bool', 'curved', "Curved Support Leg"),
                ('distance', 'curved_foot_depth', "Foot Depth", {'when': _curved}),
                ('distance', 'curved_top_band_height', "Top Band", {'when': _curved}),
                ('distance', 'curved_sweep_height', "Curve Height", {'when': _curved}),
            )}),
        ('group', 'ff_leg_depths', "Panel Depth Overrides", {'fields': (
            ('distance', 'override_left_panel_depth', "Left (0 = Auto)"),
            ('distance', 'override_right_panel_depth', "Right (0 = Auto)"),
        )}),
        ('group', 'ff_leg_nailers', "Back & Nailers", {'fields': (
            ('bool', 'include_back_left_nailer', "Left Nailer"),
            ('bool', 'include_back_right_nailer', "Right Nailer"),
            ('distance', 'back_width', "Back Width", {'when': _nailers}),
            ('distance', 'back_thickness', "Back Thickness", {'when': _nailers}),
            ('distance', 'nailer_width', "Nailer Height", {'when': _nailers}),
            ('distance', 'nailer_thickness', "Nailer Thickness", {'when': _nailers}),
        )}),
    )
    return "Leg", 'cab_parts', size, root.leg_product, options


def _shelf_height_owner(root):
    from ...operators import prop_proxy
    return prop_proxy.owner(root, 'FF_SHELF_HEIGHT')


def _floating_shelf(root):
    from . import ui_face_frame
    size = (
        ('distance', 'width', "Width"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height', "Thickness"),
    )
    options = (
        ('enum', 'shelf_type', "Type"),
        ('enum', 'edge_profile', "Edge"),
        ('distance', 'material_thickness', "Top & Bottom"),
        ('bool', 'finish_left', "Finish Left End"),
        ('bool', 'finish_right', "Finish Right End"),
        ('enum', 'corner_left', "Left Corner"),
        ('enum', 'corner_right', "Right Corner"),
        ('group', 'ff_shelf_groove', "Light Groove", {
            'when': _grooved,
            'summary': lambda s: ", ".join(
                n for n, on in (("Top", s.include_groove_top),
                                ("Bottom", s.include_groove_bottom)) if on) or "None",
            'fields': (
                ('bool', 'include_groove_top', "Top Groove"),
                ('bool', 'include_groove_bottom', "Bottom Groove"),
                ('distance', 'groove_distance_from_rear', "Top Distance", {'when': _grooving}),
                ('bool', 'groove_top_from_front', "Top From Front", {'when': _grooving}),
                ('distance', 'groove_width', "Width", {'when': _grooving}),
                ('distance', 'groove_depth', "Depth", {'when': _grooving}),
                ('bool', 'groove_bottom_separate', "Bottom Separate", {'when': _grooving}),
                ('distance', 'groove_bottom_distance', "Bottom Distance", {'when': _bottom_separate}),
                ('bool', 'groove_bottom_from_front', "Bottom From Front", {'when': _bottom_separate}),
                ('bool', 'groove_bottom_own_size', "Bottom Own Size", {'when': _grooving}),
                ('distance', 'groove_bottom_width', "Bottom Width", {'when': _bottom_own_size}),
                ('distance', 'groove_bottom_depth', "Bottom Depth", {'when': _bottom_own_size}),
            )}),
    )
    extra = (_shelf_height_owner(root), (
        ('distance', 'height', ui_face_frame.floating_shelf_height_label(root)),
    ))
    return "Floating Shelf", 'cab_parts', size, root.floating_shelf, options, extra


def _end_shelves(root):
    size = (
        ('distance', 'width', "Width"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height', "Height"),
        ('distance', 'toe_kick_height', "Kick Height", {'when': lambda cab: _kicked(cab.id_data.end_shelves)}),
        ('distance', 'toe_kick_setback', "Kick Setback", {'when': lambda cab: _kicked(cab.id_data.end_shelves)}),
    )
    options = (
        ('enum', 'rounded_side', "Open Side"),
        ('distance', 'corner_radius', "Corner Radius"),
        ('number', 'shelf_quantity', "Shelves"),
        ('bool', 'peninsula', "Peninsula", {'when': _base}),
        ('bool', 'include_back', "Finished Back",
         {'when': lambda es: not (es.kind == 'BASE' and es.peninsula)}),
    )
    return "End Shelves", 'cab_parts', size, root.end_shelves, options


def _mantle(root):
    size = (
        ('distance', 'width', "Width"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height', "Height"),
    )
    options = (
        ('enum', 'mantle_style', "Style"),
        ('enum', 'crown_profile', "Crown", {'when': _has_crown}),
        ('distance', 'top_overhang', "Top Overhang", {'when': _has_crown}),
        ('distance', 'material_thickness', "Material"),
        ('bool', 'finish_left', "Finish Left End"),
        ('bool', 'finish_right', "Finish Right End"),
        ('group', 'ff_mantle_surround', "Legs & Header", {
            'summary': lambda m: "On" if m.include_surround else "Off", 'fields': (
                ('bool', 'include_surround', "Legs & Header"),
                ('enum', 'surround_build', "Build", {'when': _surround}),
                ('distance', 'leg_width', "Leg Width", {'when': _surround}),
                ('distance', 'leg_depth', "Leg Depth", {'when': _surround}),
                ('distance', 'header_height', "Header Height", {'when': _surround}),
                ('distance', 'header_depth', "Header Depth", {'when': _surround}),
                ('bool', 'include_base_moulding', "Base Moulding", {'when': _surround}),
                ('enum', 'base_profile', "Profile", {'when': _base_moulding}),
            )}),
    )
    return "Mantle", 'cab_parts', size, root.mantle_product, options


def _valance(root):
    size = (
        ('distance', 'width', "Width"),
        ('distance', 'depth', "Depth"),
        ('distance', 'height', "Height"),
    )
    options = (
        ('distance', 'height_off_floor', "Off Floor"),
        ('distance', 'frame_thickness', "Frame Thickness"),
        ('bool', 'finish_left', "Finish Left End"),
        ('bool', 'finish_right', "Finish Right End"),
        ('bool', 'include_cover', "Include Cover"),
        ('distance', 'cover_thickness', "Cover Thickness", {'when': _cover}),
        ('bool', 'flush_bottom', "Flush Bottom", {'when': _cover}),
        ('distance', 'top_scribe', "Top Scribe", {'when': _cover_scribe}),
    )
    return "Valance", 'cab_parts', size, root.valance_product, options


def _column_beam(root):
    from . import types_column_beam
    cb = root.column_beam_product
    column = cb.orientation == 'COLUMN'
    if column:
        size = (
            ('distance', 'height', "Length"),
            ('distance', 'width', "Width"),
            ('distance', 'depth', "Depth"),
        )
    else:
        size = (
            ('distance', 'width', "Length"),
            ('distance', 'depth', "Depth"),
            ('distance', 'height', "Height"),
        )
    faces = types_column_beam.faces_for(cb.orientation)
    sides = tuple(('bool', side, label) for side, _framed, label in faces)
    framed = tuple(('bool', fr, label, {'when': lambda o, s=side: getattr(o, s)})
                   for side, fr, label in faces)
    options = (
        ('choices', 'orientation', "", {'cols': 2}),
        ('distance', 'material_thickness', "Material"),
        ('group', 'ff_cb_sides', "Sides Built", {
            'summary': lambda o: str(sum(1 for s, _f, _l in faces if getattr(o, s))),
            'fields': sides}),
        ('group', 'ff_cb_framed', "Framed Sides", {'fields': framed + (
            ('number', 'panel_count', "Panels"),
            ('distance', 'frame_stile_width', "Stile Width"),
            ('distance', 'frame_rail_width', "Rail Width"),
            ('distance', 'frame_member_thickness', "Frame Thickness"),
        )}),
        ('group', 'ff_cb_ceiling', "False Ceiling", {'when': _beam, 'fields': (
            ('bool', 'include_false_ceiling', "False Ceiling"),
            ('distance', 'false_ceiling_recess', "Recess Depth", {'when': _false_ceiling}),
            ('distance', 'false_ceiling_thickness', "Thickness", {'when': _false_ceiling}),
        )}),
    )
    label = "Column" if column else "Beam"
    return label, 'cab_parts', size, cb, options


_BUILDERS = {
    LEG_TAG: _leg,
    SHELF_TAG: _floating_shelf,
    END_SHELVES_TAG: _end_shelves,
    MANTLE_TAG: _mantle,
    VALANCE_TAG: _valance,
    COLUMN_BEAM_TAG: _column_beam,
}


# ---- The page ---------------------------------------------------------------

_opened = set()         # products whose groups were opened once this session


def _open_once(context, key):
    from ...operators import options_panel
    if key in _opened:
        return
    _opened.add(key)
    method = 'group:' + key
    if not options_panel.section_expanded(context, method):
        options_panel.toggle_section(context, method)


# ---- Loose parts ------------------------------------------------------------

def _wood_top_anchored(wt):
    return bool(wt.id_data.parent and wt.id_data.parent.get('IS_FACE_FRAME_CABINET_CAGE'))


def _wood_top_sided(wt):
    """A shaped top (its outline edited) has no four sides to pick."""
    return not wt.id_data.get('ct_outline')


def _edged(wt):
    return wt.nosing_style == 'NONE' and wt.edge_type != 'NONE'


def _edge_on(side):
    return lambda wt: _edge_side(wt) and getattr(wt, 'edge_' + side)


def _nosed(wt):
    return wt.edge_type == 'NONE' and wt.nosing_style != 'NONE'


def _edge_side(wt):
    return _edged(wt) and _wood_top_sided(wt)


def _nosing_side(wt):
    return _nosed(wt) and _wood_top_sided(wt)


def _veneer(wt):
    return wt.top_type == 'VENEER'


WOOD_TOP_FIELDS = (
    ('choices', 'top_type', "", {'cols': 2}),
    ('distance', 'thickness', "Thickness"),
    ('distance', 'width', "Width", {'when': lambda wt: not _wood_top_anchored(wt)}),
    ('distance', 'depth', "Depth", {'when': lambda wt: not _wood_top_anchored(wt)}),
    ('group', 'ff_wood_top_overhangs', "Overhangs", {'when': _wood_top_anchored, 'fields': (
        ('distance', 'overhang_front', "Front"),
        ('distance', 'overhang_back', "Back"),
        ('distance', 'overhang_left', "Left"),
        ('distance', 'overhang_right', "Right"),
    )}),
    ('group', 'ff_wood_top_edge', "Edge", {
        'when': lambda wt: wt.nosing_style == 'NONE',
        'summary': lambda wt: _enum_label(wt, 'edge_type'), 'fields': (
            ('enum', 'edge_type', "Edge"),
            ('distance', 'edge_thickness', "Thickness", {'when': _edged}),
            ('bool', 'edge_front', "Front", {'when': _edge_side}),
            ('bool', 'edge_back', "Back", {'when': _edge_side}),
            ('bool', 'edge_left', "Left", {'when': _edge_side}),
            ('bool', 'edge_right', "Right", {'when': _edge_side}),
        )}),
    ('group', 'ff_wood_top_edge_ends', "Edge Ends", {
        'when': _edge_side, 'fields': (
            ('distance', 'edge_front_trim_left', "Front - Left", {'when': _edge_on('front')}),
            ('distance', 'edge_front_trim_right', "Front - Right", {'when': _edge_on('front')}),
            ('distance', 'edge_back_trim_left', "Back - Left", {'when': _edge_on('back')}),
            ('distance', 'edge_back_trim_right', "Back - Right", {'when': _edge_on('back')}),
            ('distance', 'edge_left_trim_front', "Left - Front", {'when': _edge_on('left')}),
            ('distance', 'edge_left_trim_back', "Left - Back", {'when': _edge_on('left')}),
            ('distance', 'edge_right_trim_front', "Right - Front", {'when': _edge_on('right')}),
            ('distance', 'edge_right_trim_back', "Right - Back", {'when': _edge_on('right')}),
        )}),
    ('group', 'ff_wood_top_nosing', "Edge Profile", {
        'when': lambda wt: wt.edge_type == 'NONE',
        'summary': lambda wt: _enum_label(wt, 'nosing_style'), 'fields': (
            ('enum', 'nosing_style', "Profile"),
            ('distance', 'nosing_height', "Height", {'when': _nosed}),
            ('bool', 'nosing_front', "Front", {'when': _nosing_side}),
            ('bool', 'nosing_back', "Back", {'when': _nosing_side}),
            ('bool', 'nosing_left', "Left", {'when': _nosing_side}),
            ('bool', 'nosing_right', "Right", {'when': _nosing_side}),
        )}),
    ('group', 'ff_wood_top_lid', "Hinged Lid", {'when': _veneer, 'fields': (
        ('bool', 'hinged_lid', "Hinged Lid"),
        ('number', 'lid_stay_qty', "Lid Stays", {'when': lambda wt: wt.hinged_lid}),
        ('enum', 'hinge_finish', "Hinge Finish", {'when': lambda wt: wt.hinged_lid}),
    )}),
    ('enum', 'plan_display', "Plan Drawing"),
)


def _misc_input(name):
    from ...operators import prop_proxy
    from ...hb_types import GeoNodeCutpart

    def get(obj):
        try:
            return float(GeoNodeCutpart(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        from .operators import ops_part_commands
        GeoNodeCutpart(obj).set_input(name, float(value))
        ops_part_commands._misc_part_recarve(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0)


def _misc_key(key, default, items, rebuild_when=None):
    """A misc part's panel setting: stamped on the part, then the part
    rebuilt -- a beadboard setting only matters, and only rebuilds,
    while the part is beadboard."""
    from ...operators import prop_proxy

    def set(obj, value):
        obj[key] = str(value)
        if rebuild_when is None or obj.get('HB_MISC_PANEL_TYPE') == rebuild_when:
            part = types_face_frame.MiscPart()
            part.obj = obj
            part.rebuild()
    return prop_proxy.computed(lambda o: str(o.get(key, default)), set,
                               type='ENUM', items=items)


def _beadboard(owner):
    return owner.id_data.get('HB_MISC_PANEL_TYPE') == 'BEADBOARD'


MISC_PART_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'depth', "Depth"),
    ('distance', 'thickness', "Thickness"),
    ('enum', 'panel_type', "Type"),
    ('enum', 'beadboard_pattern', "Pattern", {'when': _beadboard}),
    ('enum', 'beadboard_material', "Material", {'when': _beadboard}),
)


def _door_input(name):
    from ...operators import prop_proxy
    from ...hb_types import GeoNodeCutpart

    def get(obj):
        try:
            return float(GeoNodeCutpart(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        from .operators import ops_part_commands
        GeoNodeCutpart(obj).set_input(name, float(value))
        ops_part_commands._rebuild_door_part(obj)
        types_face_frame.position_door_part_pull(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0)


def _door_box(key, kind, default):
    from ...operators import prop_proxy

    def get(obj):
        value = obj.get(key, default)
        return bool(value) if kind == 'BOOLEAN' else float(value)

    def set(obj, value):
        obj[key] = value
        types_face_frame.position_door_part_box(obj)
    return prop_proxy.computed(get, set, type=kind,
                               unit='LENGTH' if kind == 'FLOAT' else 'NONE',
                               precision=4)


def _drawer_front(owner):
    return owner.id_data.get('DOOR_PART_FRONT_KIND') == 'DRAWER'


def _front_kind(owner):
    return str(owner.id_data.get('DOOR_PART_FRONT_KIND', 'DOOR')).title()


DOOR_PART_FIELDS = (
    ('value', _front_kind, "Front"),
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'thickness', "Thickness"),
    ('bool', 'drawer_box', "Drawer Box", {'when': _drawer_front}),
    ('distance', 'box_depth', "Box Depth",
     {'when': lambda o: _drawer_front(o) and o.drawer_box}),
)


def _register_part_schemas():
    from ...operators import prop_proxy
    prop_proxy.register(MISC_PART_SCHEMA, {
        'width': _misc_input('Length'),
        'depth': _misc_input('Width'),
        'thickness': _misc_input('Thickness'),
        'panel_type': _misc_key('HB_MISC_PANEL_TYPE', 'PANEL', (
            ('PANEL', "Panel"), ('BEADBOARD', "Beadboard"), ('SHIPLAP', "Shiplap"),
            ('V_GROOVE', "V-Groove"), ('SLOTTED_SHELF', "Slotted Shelf"))),
        'beadboard_pattern': _misc_key('HB_MISC_BEADBOARD_PATTERN', 'STANDARD', (
            ('STANDARD', "Standard"), ('WIDE', "Wide")), rebuild_when='BEADBOARD'),
        'beadboard_material': _misc_key('HB_MISC_BEADBOARD_MATERIAL', 'SOLID', (
            ('SOLID', "Solid"), ('MDF', "MDF")), rebuild_when='BEADBOARD'),
    })
    prop_proxy.register(DOOR_PART_SCHEMA, {
        'width': _door_input('Width'),
        'height': _door_input('Length'),
        'thickness': _door_input('Thickness'),
        'drawer_box': _door_box('DOOR_PART_DRAWER_BOX', 'BOOLEAN', False),
        'box_depth': _door_box('DOOR_PART_BOX_DEPTH', 'FLOAT',
                               types_face_frame.DOOR_PART_BOX_DEPTH),
    })


def _part_blocks(context, tag, part):
    from ...operators import options_panel, prop_proxy, generic_page
    if tag == WOOD_TOP_TAG:
        key, label, owner, fields = ('ff_wood_top', "Wood Top", part.wood_top,
                                     WOOD_TOP_FIELDS)
    elif tag == MISC_PART_TAG:
        key, label, fields = 'ff_misc_part', "Misc Part", MISC_PART_FIELDS
        owner = prop_proxy.owner(part, MISC_PART_SCHEMA)
    else:
        key, label, fields = 'ff_door_part', "Door Part", DOOR_PART_FIELDS
        owner = prop_proxy.owner(part, DOOR_PART_SCHEMA)
    _open_once(context, key)
    from . import selected_card
    out = [('head', (part.name, False, None))]
    out.extend(selected_card.style_blocks(context, part, 'hb_style_section'))
    out.extend(options_panel.field_blocks(context, (
        ('group', key, label, {'icon': 'cab_parts', 'fields': fields}),
    ), owner))
    menu = generic_page.menu_id(context.active_object) or generic_page.menu_id(part)
    if menu:
        out.append(('gap', None))
        out.extend(generic_page.command_blocks(context, menu))
    return out


def blocks(context, item):
    from ...operators import options_panel, generic_page
    tag, root = item
    if tag in PART_TAGS:
        return _part_blocks(context, tag, root)
    built = _BUILDERS[tag](root)
    label, icon, size, owner, options = built[:5]
    extra = built[5] if len(built) > 5 else None
    cab = root.face_frame_cabinet
    size_key = 'ff_product_size'
    options_key = 'ff_product_' + tag.lower()
    _open_once(context, size_key)
    _open_once(context, options_key)

    out = [('head', (root.name, False, None))]
    if tag == SHELF_TAG:
        others = types_face_frame.floating_shelf_group_members(root)
        if others:
            n = len(others)
            out.append(('label', f"Linked with {n} other shel{'f' if n == 1 else 'ves'}"))
    from . import selected_card
    out.extend(selected_card.style_blocks(context, cab))
    out.extend(options_panel.field_blocks(context, (
        ('group', size_key, "Size", {'icon': 'cab_cabinet',
                                     'summary': _size_summary, 'fields': size}),
    ), cab))
    if extra is not None and options_panel.section_expanded(context, 'group:' + size_key):
        # A setting kept off the product's groups (a shelf's height is
        # the object's own Z): under the size, as if it were one of them.
        out[-1:-1] = [('indent', b) for b in
                      options_panel.field_blocks(context, extra[1], extra[0])]
    out.extend(options_panel.field_blocks(context, (
        ('group', options_key, label, {'icon': icon, 'fields': options}),
    ), owner))
    out.append(('gap', None))
    out.extend(generic_page.command_blocks(context, generic_page.menu_id(root)))
    return out


# ---- Lifecycle --------------------------------------------------------------

def _update_shelf(obj, context):
    context.view_layer.update()


def register():
    from ...operators import selected_tab, prop_proxy
    prop_proxy.register('FF_SHELF_HEIGHT', {
        'height': prop_proxy.computed(
            lambda o: float(o.location.z),
            lambda o, v: setattr(o.location, 'z', float(v)),
            unit='LENGTH', precision=4),
    }, after=_update_shelf)
    _register_part_schemas()
    # Ahead of the cabinet page: a wood top or a door part may sit on a
    # cabinet, and is what was picked.
    selected_tab.register_source(SOURCE_KEY, find, blocks, first=True)


def unregister():
    try:
        from ...operators import selected_tab, prop_proxy
        selected_tab.unregister_source(SOURCE_KEY)
        for key in ('FF_SHELF_HEIGHT', MISC_PART_SCHEMA, DOOR_PART_SCHEMA):
            prop_proxy.unregister(key)
    except Exception:
        pass
