"""A closet accessory on the viewport panel's SELECTED tab.

What an accessory offers depends on what it is: one bought at set
widths has a width to pick, one sold in finishes a finish (and, on a
hamper, a fabric that depends on the finish), a cleat its length and
hooks, a wire basket its three sizes. The accessory's dialog worked that
out as it was drawn; this page does the same from the accessory itself,
so there is nothing held in a dialog and every change shows as it is
made.

The finish and fabric lists are the ones the chosen width or size is
sold in. One saved in a finish no longer sold keeps it on the list,
marked, until the width or size is changed -- then a finish that is sold
is picked, the room's default where it can be.
"""

import bpy

from . import types_closets

SCHEMA_PREFIX = 'CL_ACCESSORY_'


def _ops():
    from .operators import ops_closet
    return ops_closet


def _acc():
    from . import accessories_closets
    return accessories_closets


def cage_of(obj):
    return types_closets.find_accessory_cage(obj)


def _def(cage):
    return _acc().get(cage.get(types_closets.PROP_ACCESSORY_KEY, ''))


def _width(cage):
    """The width the accessory has to work in: the wall length it was
    given, or its opening's."""
    if cage.get(types_closets.PROP_ACCESSORY_ON_WALL):
        return types_closets.wall_accessory_length(cage)
    return types_closets._cage_dim_x(cage.parent)


class _State:
    """What the dialog's fields read, read off the accessory: enough for
    the helpers that work out what a width or size is sold in."""

    def __init__(self, cage, acc_def):
        ops = _ops()
        self.model = str(cage.get(types_closets.PROP_ACCESSORY_MODEL, '') or '')
        if acc_def.bands and not self.model:
            items = acc_def.band_items()
            self.model = items[0][0] if items else ''
        self.basket_width = self.basket_height = self.basket_depth = '0'
        if acc_def.is_sized:
            try:
                w, h, d = types_closets.basket_values(cage, acc_def, _width(cage))
                self.basket_width = ops._size_index(acc_def.widths, w)
                self.basket_height = ops._size_index(acc_def.heights, h)
                self.basket_depth = ops._size_index(acc_def.depths, d)
            except Exception:
                pass
        self.held_color = str(cage.get(types_closets.PROP_ACCESSORY_COLOR, '') or '')
        self.held_fabric = str(cage.get(types_closets.PROP_ACCESSORY_FABRIC, '') or '')
        # What it holds was picked for the width / size it is at now.
        self.held_variant = ops._acc_variant(self, acc_def)[2]


def _offered(cage, acc_def):
    """((finishes, not-sold one), (fabrics, not-sold one)) for the
    accessory as it stands."""
    ops = _ops()
    state = _State(cage, acc_def)
    colors = (ops._acc_offered_colors(state, acc_def) if acc_def.colors
              else ([], ''))
    fabrics = (ops._acc_offered_fabrics(state, acc_def, state.held_color)
               if acc_def.fabrics else ([], ''))
    return colors, fabrics


def _keep_sold(cage, acc_def):
    """After a width, size or finish change: move the finish and fabric
    to ones that are sold, where what the accessory holds is not."""
    acc, ops = _acc(), _ops()
    room_c, room_f = acc._room_defaults(bpy.context.scene)
    state = _State(cage, acc_def)
    # Nothing is held over from another width or size.
    state.held_variant = ''
    if acc_def.colors:
        colors = ops._acc_offered_colors(state, acc_def)[0]
        if colors and state.held_color not in colors:
            cage[types_closets.PROP_ACCESSORY_COLOR] = acc._pick(
                tuple(colors), room_c, acc.FALLBACK_COLOR)[0]
    if acc_def.fabrics:
        color = str(cage.get(types_closets.PROP_ACCESSORY_COLOR, '') or '')
        fabrics = ops._acc_offered_fabrics(state, acc_def, color)[0]
        if fabrics and state.held_fabric not in fabrics:
            cage[types_closets.PROP_ACCESSORY_FABRIC] = acc._pick(
                tuple(fabrics), room_f, acc.FALLBACK_FABRIC)[0]


def _after(cage, context):
    root = types_closets.find_starter_root(cage)
    if root is not None:
        types_closets.recalculate_closet_starter(root)
    elif cage.get(types_closets.PROP_ACCESSORY_ON_WALL):
        # Out on a wall no reconciler comes past; the layout is run
        # here, and the height typed in is applied here too.
        cage.location.z = float(cage.get(types_closets.PROP_ACCESSORY_Z, 0.0))
        types_closets.layout_wall_accessory(cage)


# ---- The schema -------------------------------------------------------------
# One per set of lists on offer: an enum's items are part of its schema.

def _schema(cage, acc_def):
    from ...operators import prop_proxy as P
    acc, ops = _acc(), _ops()
    (colors, extra_c), (fabrics, extra_f) = _offered(cage, acc_def)
    bands = [(ident, label) for ident, label, _tip in acc_def.band_items()] \
        if acc_def.bands else []
    key = SCHEMA_PREFIX + str(abs(hash((
        acc_def.key, tuple(bands), tuple(colors), extra_c, tuple(fabrics),
        extra_f, tuple(acc_def.widths or ()), tuple(acc_def.heights or ()),
        tuple(acc_def.depths or ())))))
    if key in P._schemas:
        return key
    tc = types_closets

    def stored(prop, names):
        def get(obj):
            value = str(obj.get(prop, '') or '')
            return value if value in names else (names[0] if names else '')
        return get

    def enum(prop, pairs, sold=False):
        names = [ident for ident, _label in pairs]

        def set(obj, value):
            obj[prop] = value
            d = _def(obj)
            if sold and d is not None:
                _keep_sold(obj, d)
        return P.computed(stored(prop, names), set, type='ENUM', items=pairs)

    def marked(names, extra):
        return [(n, n + " (not sold)" if n == extra else n) for n in names]

    def size(prop, sizes, slot):
        pairs = [(ident, label) for ident, label, _tip in ops._size_items(sizes)]

        def get(obj):
            d = _def(obj)
            try:
                value = tc.basket_values(obj, d, _width(obj))[slot]
            except Exception:
                return '0'
            return ops._size_index(sizes, value)

        def set(obj, value):
            i = int(value)
            if 0 <= i < len(sizes):
                obj[prop] = float(sizes[i])
                d = _def(obj)
                if d is not None:
                    _keep_sold(obj, d)
        return P.computed(get, set, type='ENUM', items=pairs)

    def cleat(slot):
        def get(obj):
            return float(tc.cleat_hook_values(obj, _width(obj))[slot])
        return get

    def cleat_length_set(obj, value):
        if obj.get(tc.PROP_ACCESSORY_ON_WALL):
            # A wall cleat has no opening to follow: its length is its own.
            obj[tc.PROP_CLEAT_LENGTH] = float(value)
            return
        # Given the opening's own width, it goes back to following the
        # opening rather than being pinned to today's figure.
        follows = float(value) >= tc._cage_dim_x(obj.parent) - 1e-6
        obj[tc.PROP_CLEAT_LENGTH] = 0.0 if follows else float(value)
        if follows:
            obj[tc.PROP_CLEAT_X] = -1.0
        elif float(obj.get(tc.PROP_CLEAT_X, -1.0)) < 0.0:
            obj[tc.PROP_CLEAT_X] = float(cleat(1)(obj))

    def height_set(obj, value):
        # Below zero hangs it past the bottom of the partition. A wall
        # has no partition to hang below.
        z = float(value)
        if obj.get(tc.PROP_ACCESSORY_ON_WALL):
            z = max(z, 0.0)
        obj[tc.PROP_ACCESSORY_Z] = z

    def front_open_get(obj):
        front = ops._accessory_front(obj)
        return float(front.get('hb_drawer_open', 0.0)) * 100.0 if front is not None else 0.0

    def front_open_set(obj, value):
        front = ops._accessory_front(obj)
        if front is not None:
            front['hb_drawer_open'] = min(max(float(value), 0.0), 100.0) / 100.0

    def auto_center_set(obj, value):
        obj[tc.PROP_ACCESSORY_AUTO_CENTER] = 1 if value else 0
        d = _def(obj)
        if not value and d is not None and tc.PROP_ACCESSORY_SETBACK not in obj:
            obj[tc.PROP_ACCESSORY_SETBACK] = float(tc.accessory_setback(obj, d))

    props = {
        'custom_name': P.computed(
            lambda o: str(o.get(tc.PROP_CUSTOM_NAME, '') or ''),
            lambda o, v: o.__setitem__(tc.PROP_CUSTOM_NAME, str(v)),
            type='STRING'),
        'custom_height': P.computed(
            lambda o: float(tc.custom_accessory_height(o)),
            lambda o, v: o.__setitem__(tc.PROP_CUSTOM_HEIGHT, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'panel_location': enum(tc.PROP_ACCESSORY_PANEL_LOC, [
            (ident, label) for ident, label, _tip in acc.PANEL_LOCATIONS]),
        'auto_center': P.computed(
            lambda o: bool(tc.auto_center(o, _def(o))), auto_center_set,
            type='BOOLEAN'),
        'setback': P.computed(
            lambda o: float(tc.accessory_setback(o, _def(o))),
            lambda o, v: o.__setitem__(tc.PROP_ACCESSORY_SETBACK, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'cleat_length': P.computed(cleat(0), cleat_length_set, unit='LENGTH',
                                   precision=4, hard_min=0.0),
        'cleat_x': P.computed(
            cleat(1), lambda o, v: o.__setitem__(tc.PROP_CLEAT_X, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'cleat_height': P.computed(
            cleat(2), lambda o, v: o.__setitem__(tc.PROP_CLEAT_HEIGHT, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'hook_qty': P.computed(
            lambda o: int(cleat(3)(o)),
            lambda o, v: o.__setitem__(tc.PROP_HOOK_QTY, int(v)),
            type='INT', hard_min=0, hard_max=24),
        'hook_inset': P.computed(
            cleat(4), lambda o, v: o.__setitem__(tc.PROP_HOOK_INSET, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'opening_height': P.computed(
            lambda o: float(o.get(tc.PROP_ACCESSORY_OPEN_H, 0.0) or 0.0),
            lambda o, v: o.__setitem__(tc.PROP_ACCESSORY_OPEN_H, float(v)),
            unit='LENGTH', precision=4, hard_min=0.0),
        'remove_front': P.computed(
            lambda o: bool(o.get(tc.PROP_ACCESSORY_NO_FRONT)),
            lambda o, v: o.__setitem__(tc.PROP_ACCESSORY_NO_FRONT, 1 if v else 0),
            type='BOOLEAN'),
        'open_drawer': P.computed(front_open_get, front_open_set,
                                  hard_min=0.0, hard_max=100.0, precision=0),
        'location': P.computed(
            lambda o: float(o.get(tc.PROP_ACCESSORY_Z, 0.0)), height_set,
            unit='LENGTH', precision=4),
    }
    if bands:
        props['model'] = enum(tc.PROP_ACCESSORY_MODEL, bands, sold=True)
    if colors:
        props['color'] = enum(tc.PROP_ACCESSORY_COLOR,
                              marked(colors, extra_c), sold=True)
    if fabrics:
        props['fabric'] = enum(tc.PROP_ACCESSORY_FABRIC,
                               marked(fabrics, extra_f))
    if acc_def.is_sized:
        props['basket_width'] = size(tc.PROP_BASKET_W, acc_def.widths, 0)
        props['basket_height'] = size(tc.PROP_BASKET_H, acc_def.heights, 1)
        props['basket_depth'] = size(tc.PROP_BASKET_D, acc_def.depths, 2)
    P.register(key, props, after=_after)
    return key


# ---- The page ---------------------------------------------------------------

def _fields(cage, acc_def, owner):
    acc = _acc()
    family = acc_def.family
    on_wall = bool(cage.get(types_closets.PROP_ACCESSORY_ON_WALL))
    f = []
    if acc_def.custom:
        f += [('text', 'custom_name', "Name"),
              ('distance', 'custom_height', "Height")]
    if owner.has('model'):
        f.append(('enum', 'model', "Width"))
    if family == acc.FAMILY_PANEL:
        f.append(('enum', 'panel_location', "Mounts On"))
    if owner.has('color'):
        f.append(('enum', 'color', "Finish"))
    if owner.has('fabric'):
        f.append(('enum', 'fabric', "Fabric"))
    if family == acc.FAMILY_PANEL:
        # Where it sits front to back: it screws to a panel face, so how
        # far in from the front is a choice.
        f += [('bool', 'auto_center', "Auto Center"),
              ('distance', 'setback', "Back From The Front",
               {'when': lambda o: not o.auto_center})]
    if acc_def.is_sized:
        f.append(('group', 'cl_acc_size', "Size", {'fields': (
            ('enum', 'basket_width', "Width"),
            ('enum', 'basket_height', "Height"),
            ('enum', 'basket_depth', "Depth"),
        )}))
    if family == acc.FAMILY_CLEAT:
        cleat = [('distance', 'cleat_length', "Cleat Length")]
        if not on_wall:
            # On a wall where it is along the wall was said by placing it.
            cleat.append(('distance', 'cleat_x', "From The Left", {
                'when': lambda o: o.cleat_length
                < types_closets._cage_dim_x(o.id_data.parent) - 1e-6}))
        cleat += [('distance', 'cleat_height', "Cleat Height"),
                  ('number', 'hook_qty', "Hooks"),
                  ('distance', 'hook_inset', "In From Each End",
                   {'when': lambda o: o.hook_qty > 1})]
        f.append(('group', 'cl_acc_cleat', "Cleat & Hooks", {
            'summary': lambda o: "%d hooks" % o.hook_qty,
            'fields': tuple(cleat)}))
    if family == acc.FAMILY_INSERT:
        f += [('distance', 'opening_height', "Drawer Opening Height"),
              ('bool', 'remove_front', "Remove Drawer Front"),
              ('number', 'open_drawer', "Open Drawer (%)", {
                  'when': lambda o: not o.remove_front
                  and _ops()._accessory_front(o.id_data) is not None})]
    elif types_closets.fixed_accessory_z(cage.parent, acc_def, cage) is None:
        f.append(('distance', 'location', "Height Off Opening Floor"))
    return tuple(f)


def blocks(context, cage):
    from ...operators import options_panel, prop_proxy
    acc_def = _def(cage)
    out = [('head', (cage.name, False, None))]
    if acc_def is None:
        out.append(('note', "This accessory is no longer offered."))
        out.append(('note', "It keeps the space it was given until it is deleted."))
    else:
        if not acc_def.custom and acc_def.label:
            # Which accessory this is: the fields alone do not say.
            out.append(('value', ("Accessory", acc_def.label)))
        owner = prop_proxy.owner(cage, _schema(cage, acc_def))
        out.extend(options_panel.field_blocks(
            context, _fields(cage, acc_def, owner), owner))
        if acc_def.family == _acc().FAMILY_INSERT:
            # It stands on a shelf: where it sits is settled by placing it.
            out.append(('hint', "Height is set by placing it."))
        elif types_closets.fixed_accessory_z(cage.parent, acc_def, cage) is not None:
            out.append(('hint', "Height is set by the accessory."))
        warning = cage.get(types_closets.PROP_ACCESSORY_WARNING, '')
        if warning:
            out.append(('note', warning))
        if (_ops()._accessory_can_fit(cage, acc_def)
                and not cage.get(types_closets.PROP_ACCESSORY_ON_WALL)):
            out.append(('actions', ((
                "Fit Opening To Accessory",
                'hb_closets.fit_opening_to_accessory', {}, None),)))
    # The accessory's dialog is this page.
    from .selected_card import _actions
    _actions(context, out, cage, skip=('hb_closets.accessory_prompts',))
    return out


def unregister():
    try:
        from ...operators import prop_proxy
        for key in [k for k in prop_proxy._schemas if k.startswith(SCHEMA_PREFIX)]:
            prop_proxy.unregister(key)
    except Exception:
        pass
