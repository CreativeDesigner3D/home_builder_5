"""Frameless cabinets and products on the viewport panel's SELECTED tab.

The page reads the way the face frame cabinet's does. The title is
where the pick sits -- Cabinet > Bay 2 > Opening 1 > Door -- and a click
on a step above selects it. Under it are the cabinet's style, then tabs
that move between the cabinet and the bay, opening and part last picked
inside it, then the page for the level picked:

  Cabinet  -- size, toe kick, construction prompts
  Bay      -- its size and what its opening is built as
  Opening  -- the front, what is inside, its accessories
  Interior -- a shelf, a division or the interior itself
  Drawer   -- box construction, slides and what is in the drawer
  Part     -- a door, a side, anything with its own right-click menu

Each page ends with quick actions from the pick's right-click menu, All
Actions and the pick's own Properties dialog. Picking several cabinets
(or openings) and typing a value sets them all.

A frameless cabinet keeps its settings as custom properties and
geometry-node inputs rather than in a property group, so the fields go
through prop_proxy schemas: each write is followed by the solve the
cabinet's own dialog runs. Products (legs, panels, floating shelves,
valances ...) get their size and height off the floor.
"""

import bpy

from ... import hb_utils, hb_project, units


SOURCE_KEY = 'FRAMELESS'

CABINET_GROUP = 'fl_cabinet'
BAY_GROUP = 'fl_bay'
OPENING_GROUP = 'fl_opening'
PRODUCT_GROUP = 'fl_product'

CABINET_SCHEMA = 'FL_CABINET'
OPENING_SCHEMA = 'FL_OPENING'
PRODUCT_SCHEMA = 'FL_PRODUCT'
MISC_PART_SCHEMA = 'FL_MISC_PART'
STYLE_PREFIX = 'FL_STYLE_'
SCOPE_PREFIX = 'FL_SCOPE_'

TAG_BAY = 'IS_FRAMELESS_BAY_CAGE'
TAG_OPENING = 'IS_FRAMELESS_OPENING_CAGE'
TAG_INTERIOR = 'IS_FRAMELESS_INTERIOR_CAGE'

TOE_KICK_TYPES = ("Notch Ends to Floor", "Ladder Style", "Floating",
                  "Leg Levelers")

# Prompts that take more than a write -- a toe kick type swaps parts, a
# finished interior repaints the cabinet: the Toe Kick group and the
# dialog handle them.
_DIALOG_ONLY = ('Toe Kick Type', 'Finished Interior')


# ---- Finding what is picked -------------------------------------------------

def _owning(obj, tag):
    while obj is not None:
        if obj.get(tag):
            return obj
        obj = obj.parent
    return None


def _under(obj, root):
    o = obj.parent if obj is not None else None
    while o is not None:
        if o == root:
            return True
        o = o.parent
    return False


def _items():
    from . import interior_items
    return interior_items


def _is_drawer_part(obj):
    return bool(obj.get('IS_DRAWER_BOX') or obj.get('IS_DRAWER_FRONT')
                or obj.get('IS_PULLOUT_FRONT'))


def _is_interior_part(obj):
    return bool(obj.get(TAG_INTERIOR) or obj.get('IS_FRAMELESS_INTERIOR_PART')
                or obj.get('IS_FRAMELESS_INTERIOR_SECTION')
                or hb_utils.get_interior_bp(obj) is not None)


def find(context):
    """(kind, root, bay, opening, part) for a picked frameless cabinet or
    part of one, or ('product', root, None, None, None), or None. `kind`
    is the level the page is on: 'cabinet', 'bay', 'opening',
    'interior' (the interior, a section or a shelf: `part`), 'drawer'
    (a drawer or pull-out's front or box: `part`, with `opening` the
    drawer's opening) or 'part' -- anything else with a right-click
    menu of its own."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    root = hb_utils.get_cabinet_bp(obj)
    if root is None:
        return None
    if 'IS_FRAMELESS_PRODUCT_CAGE' in root:
        return ('product', root, None, None, None)
    if obj == root:
        return ('cabinet', root, None, None, None)
    bay = _owning(obj, TAG_BAY)
    bay = bay if _under(bay, root) else None
    opening = _owning(obj, TAG_OPENING)
    opening = opening if _under(opening, root) else None
    if obj.get(TAG_BAY):
        return ('bay', root, obj, None, None)
    if obj.get(TAG_OPENING):
        return ('opening', root, bay, obj, None)
    if _is_drawer_part(obj):
        drawer = _items().drawer_opening_for(obj)
        if drawer is not None:
            return ('drawer', root, bay, drawer, obj)
    if _is_interior_part(obj):
        return ('interior', root, bay, opening, obj)
    from ...operators import generic_page
    if generic_page.menu_id(obj):
        return ('part', root, bay, opening, obj)
    # A piece with no menu of its own reads as the level that holds it.
    if opening is not None:
        return ('opening', root, bay, opening, None)
    if bay is not None:
        return ('bay', root, bay, None, None)
    return ('cabinet', root, None, None, None)


# ---- Several picked at once -------------------------------------------------
# Picking five cabinets and typing a depth sets all five. The page shows
# the active one; the others of the same kind in the selection are its
# peers, which the field engine reads for "Mixed" and writes along with
# it. Gathered once per page build -- the engine asks for every field.

_picked = {'cabinet': [], 'opening': [], 'product': [], 'drawer': []}


def _gather(context):
    roots, openings, products, drawers = [], [], [], []
    for obj in context.selected_objects:
        root = hb_utils.get_cabinet_bp(obj)
        if root is None:
            continue
        if 'IS_FRAMELESS_PRODUCT_CAGE' in root:
            if root not in products:
                products.append(root)
            continue
        if root not in roots:
            roots.append(root)
        if obj.get(TAG_OPENING):
            openings.append(obj)
        elif _is_drawer_part(obj):
            drawer = _items().drawer_opening_for(obj)
            if drawer is not None and drawer not in drawers:
                drawers.append(drawer)
    _picked.update({'cabinet': roots, 'opening': openings,
                    'product': products, 'drawer': drawers})


def _peer_kind(key):
    if key in (CABINET_SCHEMA,) or key.startswith(STYLE_PREFIX):
        return 'cabinet'
    if key == OPENING_SCHEMA:
        return 'opening'
    if key in (PRODUCT_SCHEMA, MISC_PART_SCHEMA):
        return 'product'
    return None


def _peers(owner):
    """The other picked objects of the owner's kind, seen through the
    same schema -- none unless the owner is itself one of the picked."""
    from ...operators import prop_proxy
    try:
        path = owner.path_from_id()
        obj = owner.id_data
    except Exception:
        return ()
    if not path.startswith(prop_proxy.PATH_PREFIX):
        return ()
    key = path[len(prop_proxy.PATH_PREFIX):]
    kind = _peer_kind(key)
    if kind is None:
        return ()
    objs = _picked.get(kind, ())
    try:
        if obj not in objs:
            return ()
        return [prop_proxy.owner(o, key) for o in objs
                if o != obj and o.name in bpy.data.objects]
    except ReferenceError:
        return ()           # one was deleted since the page was built


def _count(kind):
    return len(_picked.get(kind, ()))


# ---- Summaries and conditions ----------------------------------------------

def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


def _size_summary(owner):
    return f"{_dist(owner.width)} x {_dist(owner.height)} x {_dist(owner.depth)}"


def _has(key):
    return lambda owner: key in owner.id_data


def _hung(owner):
    return owner.id_data.get('CABINET_TYPE') == 'UPPER'


def _kicked(owner):
    return 'Toe Kick Height' in owner.id_data


def _kick_panel(owner):
    return _kicked(owner) and bool(owner.id_data.get('Toe Kick Panel'))


def _bay_size(bay_obj):
    from ...hb_types import GeoNodeObject
    try:
        node = GeoNodeObject(bay_obj)
        return f"{_dist(node.get_input('Dim X'))} x {_dist(node.get_input('Dim Z'))}"
    except Exception:
        return None


def _door(owner):
    return 'Door Swing' in owner.id_data


def _flip_up(owner):
    return any(c.get('IS_FLIP_UP_DOOR') for c in owner.id_data.children)


# ---- Schemas ----------------------------------------------------------------

def _solve(obj, context):
    hb_utils.run_calc_fix(context, obj)


def _solve_product(obj, context):
    from . import types_products
    types_products.recalculate_product(obj)
    if obj.get('PART_TYPE') == 'SUPPORT_FRAME':
        from .operators import ops_products
        tl = ops_products._turned_leg()
        if tl.LEG_STYLE_PROP in obj:
            tl.sync_frame_legs(obj)


def _toe_kick_type():
    from ...operators import prop_proxy

    def get(obj):
        try:
            return str(int(obj.get('Toe Kick Type', 0)))
        except (TypeError, ValueError):
            return '0'

    def set(obj, value):
        from . import types_frameless
        if int(value) != int(obj.get('Toe Kick Type', 0)):
            types_frameless.set_toe_kick_type(obj, int(value))
    return prop_proxy.computed(
        get, set, type='ENUM',
        items=[(str(i), label) for i, label in enumerate(TOE_KICK_TYPES)])


def _register_schemas():
    from ...operators import prop_proxy as P
    P.register(CABINET_SCHEMA, {
        'width': P.node_input('Dim X'),
        'depth': P.node_input('Dim Y'),
        'height': P.node_input('Dim Z'),
        'height_off_floor': P.height_off_floor(),
        'toe_kick_type': _toe_kick_type(),
        'toe_kick_height': P.length('Toe Kick Height'),
        'toe_kick_setback': P.length('Toe Kick Setback'),
        'flush_toe_kick': P.flag('Flush Toe Kick'),
        'toe_kick_panel': P.flag('Toe Kick Panel'),
        'toe_kick_panel_thickness': P.length('Toe Kick Panel Thickness', units.inch(0.375)),
        'toe_kick_end_inset': P.length('Toe Kick End Inset'),
        'remove_bottom': P.flag('Remove Bottom'),
    }, after=_solve)
    P.register(OPENING_SCHEMA, {
        'door_swing': P.index_enum('Door Swing', ("Left", "Right", "Double"), 2),
        'door_mechanism': P.index_enum('Door Mechanism', ("Standard", "Retracting")),
        'lift_mechanism': P.index_enum('Lift Mechanism', (
            "Stay Lift", "Bi-Fold Lift", "Up and Over", "Vertical Lift")),
        'inset_front': P.flag('Inset Front'),
        'half_overlay_top': P.flag('Half Overlay Top'),
        'half_overlay_bottom': P.flag('Half Overlay Bottom'),
        'half_overlay_left': P.flag('Half Overlay Left'),
        'half_overlay_right': P.flag('Half Overlay Right'),
    }, after=_solve)
    P.register(PRODUCT_SCHEMA, {
        'width': P.node_input('Dim X'),
        'depth': P.node_input('Dim Y'),
        'height': P.node_input('Dim Z'),
        'height_off_floor': P.height_off_floor(),
    }, after=_solve_product)
    # A misc part is a cut part: its size is length, width and thickness.
    P.register(MISC_PART_SCHEMA, {
        'width': P.node_input('Length'),
        'depth': P.node_input('Width'),
        'height': P.node_input('Thickness'),
        'height_off_floor': P.height_off_floor(),
    }, after=_solve_product)


def _unregister_schemas():
    from ...operators import prop_proxy
    for key in (CABINET_SCHEMA, OPENING_SCHEMA, PRODUCT_SCHEMA, MISC_PART_SCHEMA):
        prop_proxy.unregister(key)


# ---- Fields -----------------------------------------------------------------

CABINET_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('distance', 'height_off_floor', "Above Floor", {'when': _hung}),
    ('group', 'fl_cab_kick', "Toe Kick", {'icon': 'cab_construction', 'when': _kicked, 'fields': (
        ('enum', 'toe_kick_type', "Type"),
        ('distance', 'toe_kick_height', "Height"),
        ('distance', 'toe_kick_setback', "Setback"),
        ('bool', 'flush_toe_kick', "Flush Toe Kick"),
        ('bool', 'toe_kick_panel', "Kick Panel"),
        ('distance', 'toe_kick_panel_thickness', "Panel Thickness", {'when': _kick_panel}),
        ('distance', 'toe_kick_end_inset', "Hold In From Ends"),
    )}),
    ('bool', 'remove_bottom', "Remove Bottom", {'when': _has('Remove Bottom')}),
)

OPENING_FIELDS = (
    ('enum', 'door_swing', "Door Swing", {'when': _door}),
    ('enum', 'door_mechanism', "Mechanism", {'when': _door}),
    ('enum', 'lift_mechanism', "Lift", {'when': _flip_up}),
    ('bool', 'inset_front', "Inset Front", {'when': _has('Inset Front')}),
    ('group', 'fl_opening_overlays', "Half Overlays", {
        'when': _has('Half Overlay Top'),
        'summary': lambda o: ", ".join(
            n for n, p in (("Top", 'half_overlay_top'), ("Bottom", 'half_overlay_bottom'),
                           ("Left", 'half_overlay_left'), ("Right", 'half_overlay_right'))
            if getattr(o, p)) or "None",
        'fields': (
            ('bool', 'half_overlay_top', "Top"),
            ('bool', 'half_overlay_bottom', "Bottom"),
            ('bool', 'half_overlay_left', "Left"),
            ('bool', 'half_overlay_right', "Right"),
        )}),
)

PRODUCT_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
    ('distance', 'height_off_floor', "Above Floor"),
)


# ---- Style ------------------------------------------------------------------
# The cabinet style leads every cabinet page, whatever part is picked: it
# is the cabinet's, and switching it here saves a trip to the styles.

def _styles():
    try:
        return list(hb_project.get_main_scene().hb_frameless.cabinet_styles)
    except Exception:
        return []


def _style_schema(names):
    from ...operators import prop_proxy
    key = STYLE_PREFIX + str(abs(hash(tuple(names))))

    def get(obj):
        name = obj.get('CABINET_STYLE_NAME')
        if name in names:
            return name
        try:
            return names[int(obj.get('CABINET_STYLE_INDEX', 0))]
        except (TypeError, ValueError, IndexError):
            return names[0]

    def set(obj, value):
        styles = _styles()
        index = next((i for i, s in enumerate(styles) if s.name == value), -1)
        if index < 0 or obj.get('CABINET_STYLE_NAME') == value:
            return
        obj['CABINET_STYLE_INDEX'] = index
        obj['CABINET_STYLE_NAME'] = value
        styles[index].assign_style_to_cabinet(obj)
    if key not in prop_proxy._schemas:
        prop_proxy.register(key, {
            'style': prop_proxy.computed(
                get, set, type='ENUM', items=[(n, n) for n in names]),
        })
    return key


def style_blocks(context, root):
    """The Style row: which style the cabinet carries, switched in
    place. Nothing while the project has no styles."""
    from ...operators import options_panel, prop_proxy
    names = [s.name for s in _styles()]
    if not names:
        return []
    return options_panel.field_blocks(context, (
        ('enum', 'style', "Style"),
    ), prop_proxy.owner(root, _style_schema(names)))


# ---- Labels -----------------------------------------------------------------

def _index_label(obj, tag, word):
    """Bay N / Opening N, counted the way they stand: bays left to right,
    openings top down, among the ones the parent holds."""
    parent = obj.parent
    if parent is None:
        return word
    peers = [o for o in parent.children if o.get(tag)]
    if len(peers) < 2:
        return word
    if word == "Bay":
        peers.sort(key=lambda o: o.matrix_world.translation.x)
    else:
        peers.sort(key=lambda o: -o.matrix_world.translation.z)
    return f"{word} {peers.index(obj) + 1}"


def _type_label(root):
    kind = (root.get('CABINET_TYPE') or root.get('PART_TYPE') or "")
    return str(kind).replace('_', ' ').title()


def _part_label(part_obj):
    if part_obj.get('IS_DRAWER_BOX'):
        return "Drawer Box"
    if part_obj.get('IS_DRAWER_FRONT'):
        return "Drawer"
    if part_obj.get('IS_PULLOUT_FRONT'):
        return "Pullout"
    if part_obj.get('IS_CABINET_FRONT'):
        return "Door"
    if part_obj.get(TAG_INTERIOR):
        return "Interior"
    if part_obj.get('IS_FRAMELESS_INTERIOR_SECTION'):
        return "Section"
    role = str(part_obj.get('hb_part_role', '') or '')
    if 'SHELF' in role:
        return "Shelf"
    if role:
        return role.replace('_', ' ').title()
    return "Part"


def _interior_of(opening_obj):
    for child in opening_obj.children:
        if child.get(TAG_INTERIOR):
            return child
    return None


def _interior_summary(interior):
    """What is inside, in a few words."""
    if interior is None:
        return "Empty"
    ii = _items()
    if ii.is_items_interior(interior):
        kinds = []
        for it in ii.item_props(interior).interior_items:
            word = str(it.kind).replace('_', ' ').title()
            if word not in kinds:
                kinds.append(word)
        return ", ".join(kinds) or "Empty"
    sections = [c for c in interior.children
                if c.get('IS_FRAMELESS_INTERIOR_SECTION')]
    if sections:
        return "%d sections" % len(sections)
    if 'Shelf Quantity' in interior:
        n = int(interior.get('Shelf Quantity', 0))
        return "%d Shelf" % n if n == 1 else "%d Shelves" % n
    return interior.name.split('.')[0]


# ---- Actions ----------------------------------------------------------------

def _act(label, op_id, kwargs=None, icon=None):
    return (label, op_id, dict(kwargs or {}), None, 1.0, icon)


def _menu(label, menu_id, icon=None):
    """A button that drops down one of the right-click menu's own lists."""
    from ...operators import generic_page
    return (label + "  ›", generic_page._opener(menu_id, label), None, None,
            1.0, icon)


def _menu_actions(context, obj, skip=(), limit=6):
    """The first commands of `obj`'s right-click menu, as buttons. Add
    Accessory is left out: the page's Accessories list has it."""
    from ...operators import generic_page
    skip = tuple(skip) + ('hb_frameless.add_opening_accessory',)
    menu = generic_page.menu_id(obj)
    picked = []
    if not menu:
        return picked
    for rec in generic_page._record(context, menu):
        if rec[0] == 'op':
            if rec[2] in skip:
                continue
            label = (rec[1] or generic_page._op_label(rec[2])).rstrip('.')
            picked.append((label, rec[2], dict(rec[3]._values), None))
        elif rec[0] == 'menu':
            if rec[2] in skip:
                continue
            picked.append(_menu(rec[1] or generic_page._menu_label(rec[2]),
                                rec[2]))
        elif rec[0] == 'enum':
            label = rec[1] or generic_page._op_label(rec[2])
            picked.append((label + "  ›", generic_page._enum_opener(rec[2], rec[3]),
                           None, None, 1.0, None))
        if len(picked) == limit:
            break
    return picked


def _quick(out, picked, title="Quick Actions"):
    if not picked:
        return
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.append(('label', title))
    for i in range(0, len(picked), 2):
        out.append(('actions', tuple(picked[i:i + 2])))


def _footer(out, prompts_op):
    row = [("All Actions", 'home_builder.all_actions', None, None)]
    if prompts_op:
        row.append(("Properties…", prompts_op, None, None))
    if out and out[-1] != ('gap', None):
        out.append(('gap', None))
    out.append(('actions', tuple(row)))


# ---- Accessories ------------------------------------------------------------

_add_open = set()       # hosts whose Add Accessory fold is open


def _toggler(name):
    def toggle():
        if name in _add_open:
            _add_open.discard(name)
        else:
            _add_open.add(name)
    return toggle


def _accessory_rows(out, hosts, where):
    rows = 0
    for host in hosts:
        for index, item in _items().opening_accessories(host):
            text = item.accessory_label or item.accessory_code
            if len(hosts) > 1:
                text = "%s  (%s)" % (text, host.name)
            out.append(('list_row', {
                'key': 'flacc:%s:%d' % (host.name, index),
                'text': text,
                'summary': item.accessory_code,
                'remove': ('hb_frameless.remove_opening_accessory',
                           {'host_name': host.name, 'index': index}),
                'remove_tip': "Remove Accessory",
                'confirm': False,
            }))
            rows += 1
    if not rows:
        out.append(('note', "None in %s." % where))


def _add_fold(context, out, key, hosts, label):
    from ..face_frame import accessory_place
    name = key + ':' + "|".join(h.name for h in hosts)
    open_ = name in _add_open
    out.append(('section', (label, 'fl_add_accessory:' + name, open_,
                            _toggler(name))))
    if open_:
        out.extend(('indent', b) for b in
                   accessory_place.browse_blocks(context, key, hosts))


def accessory_blocks(context, obj):
    """The catalog accessories kept on the door or open opening (or the
    division section) `obj` sits in, each with a remove button, and the
    catalog to add from. Nothing outside such an opening."""
    ii = _items()
    host = ii.accessory_host(obj)
    if host is None:
        return []
    has_catalog = bool(ii.catalog_for(host))
    if not has_catalog and not ii.opening_accessories(host):
        return []
    out = [('gap', None), ('label', "Accessories")]
    _accessory_rows(out, [host], "this opening")
    if has_catalog:
        _add_fold(context, out, 'opening', [host], "Add Accessory")
    return out


# ---- The pages --------------------------------------------------------------

def _size_value(context, obj):
    from ...operators import generic_page
    size = generic_page._size_text(context, obj)
    if not size and any(obj.dimensions):
        us = context.scene.unit_settings
        size = "  x  ".join(units.unit_to_string(us, d) for d in obj.dimensions)
    return ('value', ("Size (W x D x H)", size)) if size else None


def _cabinet_page(context, out, root):
    from ...operators import options_panel, prop_proxy, generic_page
    label = _type_label(root)
    out.extend(options_panel.field_blocks(context, (
        ('group', CABINET_GROUP, f"Cabinet  ({label})" if label else "Cabinet",
         {'icon': 'cab_cabinet', 'summary': _size_summary,
          'fields': CABINET_FIELDS}),
    ), prop_proxy.owner(root, CABINET_SCHEMA)))
    out.extend(generic_page.prompt_blocks(
        context, root, 'fl_cabinet_prompts', "All Cabinet Prompts",
        open_first=False, exclude=_DIALOG_ONLY))
    _quick(out, _menu_actions(context, root,
                              skip=('hb_frameless.cabinet_prompts',)))
    _footer(out, 'hb_frameless.cabinet_prompts')


def _bay_page(context, out, bay_obj, title):
    from ...operators import options_panel, generic_page
    out.extend(options_panel.field_blocks(context, (
        ('value', lambda _o, b=bay_obj: _bay_size(b), "Size"),
    ), bay_obj))
    out.extend(generic_page.prompt_blocks(
        context, bay_obj, 'fl_bay_prompts', "Bay Prompts", open_first=False))
    _quick(out, _menu_actions(context, bay_obj))
    _footer(out, None)


def _opening_page(context, out, opening_obj):
    from ...operators import options_panel, prop_proxy, generic_page
    out.extend(options_panel.field_blocks(
        context, OPENING_FIELDS, prop_proxy.owner(opening_obj, OPENING_SCHEMA)))
    # What is inside, said here; changed from the menu beside it.
    interior = _interior_of(opening_obj)
    if _items().drawer_opening_for(opening_obj) is None:
        out.append(('value', ("Interior", _interior_summary(interior))))
    menus = []
    if hasattr(bpy.types, 'HOME_BUILDER_MT_opening_change'):
        menus.append(_menu("Change Opening", 'HOME_BUILDER_MT_opening_change'))
    if (interior is not None or _items().accessory_host(opening_obj) is not None) \
            and hasattr(bpy.types, 'HOME_BUILDER_MT_interior_change'):
        menus.append(_menu("Change Interior", 'HOME_BUILDER_MT_interior_change'))
    if menus:
        out.append(('actions', tuple(menus)))
    if interior is not None:
        out.append(('actions', (
            ("Interior Options", 'hb_frameless.interior_prompts', None, None),)))
    out.extend(accessory_blocks(context, opening_obj))
    _quick(out, _menu_actions(context, opening_obj, skip=(
        'hb_frameless.opening_prompts', 'HOME_BUILDER_MT_opening_change',
        'HOME_BUILDER_MT_interior_change')))
    _footer(out, 'hb_frameless.opening_prompts')


def _interior_page(context, out, part_obj):
    from ...operators import generic_page
    interior = (part_obj if part_obj.get(TAG_INTERIOR)
                else hb_utils.get_interior_bp(part_obj))
    out.append(('value', ("Interior", _interior_summary(interior))))
    if not part_obj.get(TAG_INTERIOR) and not part_obj.get(
            'IS_FRAMELESS_INTERIOR_SECTION'):
        size = _size_value(context, part_obj)
        if size:
            out.append(size)
    if hasattr(bpy.types, 'HOME_BUILDER_MT_interior_change'):
        out.append(('actions', (_menu("Change Interior",
                                      'HOME_BUILDER_MT_interior_change'),)))
    if interior is not None:
        out.extend(generic_page.prompt_blocks(
            context, interior, 'fl_interior_prompts', "Interior"))
    out.extend(accessory_blocks(context, part_obj))
    _quick(out, _menu_actions(context, part_obj, skip=(
        'hb_frameless.interior_prompts', 'HOME_BUILDER_MT_interior_change')))
    _footer(out, 'hb_frameless.interior_prompts' if interior is not None else None)


def _drawer_page(context, out, part_obj, drawers):
    """The drawer's size, box construction and slides, its commands and
    what is in it -- the face frame Drawer page, on frameless drawers."""
    from ..face_frame import accessory_place
    ops_cabinet = accessory_place.ops_cabinet
    one = len(drawers) <= 1
    if one:
        size = _size_value(context, part_obj)
        if size:
            out.append(size)
    options = ops_cabinet.drawer_box_construction_options()
    if options:
        out.append(accessory_place._option_pick(
            'CONSTRUCTION', "Construction", options,
            ops_cabinet.drawer_box_construction_label, drawers))
    options = ops_cabinet.drawer_slides_options()
    if options:
        out.append(accessory_place._option_pick(
            'SLIDES', "Slides", options, ops_cabinet.drawer_slides_label,
            drawers))
    if one:
        out.append(('gap', None))
        out.append(('actions', (
            ("Drawer Interior", 'hb_frameless.drawer_interior', None, None),
            ("Open / Close", 'hb_frameless.toggle_front_open', None, None))))
        if any(c.get('IS_PULLOUT_FRONT') for c in drawers[0].children):
            out.append(('actions', (
                ("Pullout Model", 'hb_frameless.pullout_model', None, None),)))
    out.append(('gap', None))
    out.append(('label', "Accessories"))
    _accessory_rows(out, drawers, "this drawer" if one else "these drawers")
    _add_fold(context, out, 'drawer', drawers,
              "Add Accessory" if one
              else "Add Accessory to %d Drawers" % len(drawers))
    if one:
        _quick(out, _menu_actions(context, part_obj, skip=(
            'hb_frameless.drawer_interior', 'hb_frameless.toggle_front_open',
            'hb_frameless.door_front_prompts')))
    _footer(out, 'hb_frameless.door_front_prompts'
            if part_obj.get('IS_CABINET_FRONT') else 'hb_frameless.opening_prompts')


def _part_page(context, out, part_obj):
    size = _size_value(context, part_obj)
    if size:
        out.append(size)
    front = bool(part_obj.get('IS_CABINET_FRONT'))
    if front:
        out.extend(accessory_blocks(context, part_obj))
    _quick(out, _menu_actions(context, part_obj,
                              skip=('hb_frameless.door_front_prompts',)))
    _footer(out, 'hb_frameless.door_front_prompts' if front else None)


def _product_page(context, out, root):
    from ...operators import options_panel, prop_proxy, generic_page
    if root.get('IS_FACE_FRAME_PRODUCT_CAGE'):
        # A face frame product built on frameless parts (a Half Wall,
        # a Support Frame) wears the face frame cabinet styles.
        from ..face_frame import selected_card as ff_card
        out.extend(ff_card.style_blocks(context, root, 'hb_style_section'))
    schema = (MISC_PART_SCHEMA if root.get('IS_FRAMELESS_MISC_PART')
              else PRODUCT_SCHEMA)
    label = _type_label(root)
    out.extend(options_panel.field_blocks(context, (
        ('group', PRODUCT_GROUP, label or "Product",
         {'icon': 'cab_parts', 'summary': _size_summary, 'fields': PRODUCT_FIELDS}),
    ), prop_proxy.owner(root, schema)))
    out.extend(generic_page.prompt_blocks(context, root, 'fl_product_prompts',
                                          "Options"))
    _quick(out, _menu_actions(context, root))
    _footer(out, None)


# ---- Scope: which level of the cabinet the page is on ----------------------
# The tabs under the style move between the cabinet and the bay, opening
# and part last picked inside it, selecting that level the way the
# breadcrumb does -- so a bay's page is one click from its cabinet's and
# back, without finding the bay in the viewport again.

SCOPE_LEVELS = ('Cabinets', 'Bays', 'Openings', 'Parts')
_chain = {}             # cabinet name -> {level: object name}
_scope_now = 'Cabinets'


def _remember(root, bay_obj, opening_obj, part_obj):
    """Note the levels picked inside `root`, dropping any remembered
    below a level that has just changed. Returns the picked level."""
    chain = _chain.setdefault(root.name, {})
    picked = {'Cabinets': root, 'Bays': bay_obj, 'Openings': opening_obj,
              'Parts': part_obj}
    deepest = 0
    for i, level in enumerate(SCOPE_LEVELS):
        obj = picked[level]
        if obj is None:
            continue
        deepest = i
        if chain.get(level) != obj.name:
            for lower in SCOPE_LEVELS[i + 1:]:
                if picked[lower] is None:
                    chain.pop(lower, None)
        chain[level] = obj.name
    # What is remembered must still be in this cabinet.
    for level in SCOPE_LEVELS[1:]:
        name = chain.get(level)
        obj = bpy.data.objects.get(name) if name else None
        if obj is None or hb_utils.get_cabinet_bp(obj) != root:
            chain.pop(level, None)
    return SCOPE_LEVELS[deepest]


def _scope_level(part_obj):
    """The selection mode a remembered part is picked in."""
    if part_obj is not None and part_obj.get('IS_FRAMELESS_INTERIOR_PART'):
        return 'Interiors'
    return 'Parts'


def _scope_schema(levels, labels):
    from ...operators import prop_proxy
    key = SCOPE_PREFIX + '_'.join(levels) + '_' + labels[-1]

    def get(_obj):
        return _scope_now

    def set(obj, value):
        name = _chain.get(obj.name, {}).get(value)
        if not name:
            return
        level = value
        if value == 'Parts':
            level = _scope_level(bpy.data.objects.get(name))
        bpy.ops.hb_frameless.select_level(name=name, level=level)
    if key not in prop_proxy._schemas:
        prop_proxy.register(key, {
            'scope': prop_proxy.computed(
                get, set, type='ENUM', items=list(zip(levels, labels))),
        })
    return key


def _scope_blocks(context, root, current):
    """The level tabs: Cabinet, then each level picked inside it."""
    from ...operators import options_panel, prop_proxy
    global _scope_now
    chain = _chain.get(root.name, {})
    levels = [level for level in SCOPE_LEVELS if chain.get(level)]
    if len(levels) < 2:
        return []
    labels = [_part_label(bpy.data.objects[chain[level]]) if level == 'Parts'
              else level[:-1] for level in levels]
    _scope_now = current
    key = _scope_schema(levels, labels)
    return options_panel.field_blocks(context, (
        ('choices', 'scope', "", {'cols': len(levels)}),
    ), prop_proxy.owner(root, key))


# ---- The page ---------------------------------------------------------------

def _trail(root, bay_obj, opening_obj, part_obj):
    trail = [root.name]
    if bay_obj is not None:
        trail.append(_index_label(bay_obj, TAG_BAY, "Bay"))
    if opening_obj is not None:
        trail.append(_index_label(opening_obj, TAG_OPENING, "Opening"))
    if part_obj is not None:
        trail.append(_part_label(part_obj))
    return trail


def _several(kind):
    """How many of the pick's kind are picked, when it is more than one."""
    n = _count({'cabinet': 'cabinet', 'opening': 'opening',
                'product': 'product', 'drawer': 'drawer'}.get(kind, ''))
    return n if n > 1 else 0


def blocks(context, item):
    kind, root, bay_obj, opening_obj, part_obj = item
    _gather(context)

    if kind == 'product':
        n = _several('product')
        out = ([('head', (f"{n} Products", False, None)),
                ('label', f"Changes apply to all {n}")] if n
               else [('head', (root.name, False, None))])
        _product_page(context, out, root)
        return out

    level = _remember(root, bay_obj, opening_obj, part_obj)
    trail = _trail(root, bay_obj, opening_obj, part_obj)
    n = _several(kind)
    if n:
        word = {'cabinet': "Cabinets", 'opening': "Openings",
                'drawer': "Drawers"}[kind]
        out = [('head', (f"{n} {word}", False, None)),
               ('label', f"Changes apply to all {n}")]
    else:
        out = [('head', (" › ".join(trail), False, None))]

    out.extend(style_blocks(context, root))
    if not n:
        out.extend(_scope_blocks(context, root, level))
    out.append(('gap', None))

    if kind == 'cabinet':
        _cabinet_page(context, out, root)
    elif kind == 'bay':
        _bay_page(context, out, bay_obj, trail[-1])
    elif kind == 'opening':
        _opening_page(context, out, opening_obj)
    elif kind == 'interior':
        _interior_page(context, out, part_obj)
    elif kind == 'drawer':
        drawers = list(_picked['drawer']) or [opening_obj]
        if opening_obj in drawers:
            drawers.remove(opening_obj)
            drawers.insert(0, opening_obj)
        _drawer_page(context, out, part_obj, drawers)
    else:
        _part_page(context, out, part_obj)
    return out


def crumbs(context, item):
    """Cabinet, bay, opening, part: each step above the pick selects
    that level. None while several are picked -- the head says how
    many."""
    kind, root, bay_obj, opening_obj, part_obj = item
    if kind == 'product':
        return None
    _gather(context)
    if _several(kind):
        return None
    op = 'hb_frameless.select_level'
    out = [(root.name, (op, {'name': root.name, 'level': 'Cabinets'}))]
    if bay_obj is not None:
        out.append((_index_label(bay_obj, TAG_BAY, "Bay"),
                    (op, {'name': bay_obj.name, 'level': 'Bays'})))
    if opening_obj is not None:
        out.append((_index_label(opening_obj, TAG_OPENING, "Opening"),
                    (op, {'name': opening_obj.name, 'level': 'Openings'})))
    if part_obj is not None:
        out.append((_part_label(part_obj), None))
    # The last is the pick itself: named, not a click.
    out[-1] = (out[-1][0], None)
    return out


class hb_frameless_OT_select_level(bpy.types.Operator):
    """Pick this cabinet, bay, opening or part, moving the selection mode
    to its level"""
    bl_idname = "hb_frameless.select_level"
    bl_label = "Select"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()  # type: ignore
    level: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        from . import drill_frameless as drill
        obj = context.view_layer.objects.get(self.name)
        props = getattr(context.scene, 'hb_frameless', None)
        if obj is None or props is None or self.level not in drill.RANK:
            return {'CANCELLED'}
        # Still below the mode bar's level: the drill holds. At or above
        # it, the drill has come all the way back out.
        base = drill.base_level()
        if base is None or drill.RANK[self.level] <= drill.RANK[base]:
            base = None
        drill.set_mode(context, self.level)
        drill.set_base(base)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


# ---- Lifecycle --------------------------------------------------------------

def register():
    bpy.utils.register_class(hb_frameless_OT_select_level)
    _register_schemas()
    from ...operators import selected_tab, options_panel
    selected_tab.register_source(SOURCE_KEY, find, blocks, crumbs)
    options_panel.register_peers(_peers)


def unregister():
    try:
        from ...operators import selected_tab, options_panel
        options_panel.unregister_peers(_peers)
        selected_tab.unregister_source(SOURCE_KEY)
    except Exception:
        pass
    _unregister_schemas()
    try:
        from ...operators import prop_proxy
        for key in [k for k in prop_proxy._schemas
                    if k.startswith((STYLE_PREFIX, SCOPE_PREFIX))]:
            prop_proxy.unregister(key)
    except Exception:
        pass
    bpy.utils.unregister_class(hb_frameless_OT_select_level)
