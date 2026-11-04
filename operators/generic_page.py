"""The page for a pick that has no page of its own.

Every product carries a right-click menu (its MENU_ID): its prompts
dialog, its changes, duplicate, delete. Until a library lays out a page
for a product, the SELECTED tab shows that menu here -- read off the
menu's own draw, so the page has exactly the commands the right-click
has, in the same order, and keeps up when the menu changes.

The menu's draw is run against a stand-in layout that records what it
asks for: commands become buttons, submenus and enum menus become
buttons that open a list of their commands.

Above the commands are the product's prompts: the custom properties a
product declares as its settings (``add_property``, which marks each
HOME_BUILDER_PROP), shown as fields -- a distance, a checkbox, one of a
list -- and followed by the same solve its dialog runs.
"""
import time

import bpy


# ---- Which pick -----------------------------------------------------------------

def menu_id(obj):
    """The right-click menu `obj` shows, as ui/menu_apend picks it."""
    if obj is None:
        return ""
    menu = obj.get("MENU_ID", "") or ""
    if not menu:
        from .. import cutters
        if cutters.is_cutter(obj):
            menu = cutters.MENU_ID
        elif obj.get('IS_FLOOR_BP') or obj.get('IS_CEILING_BP'):
            menu = "HOME_BUILDER_MT_floor_ceiling_commands"
    return menu if menu and hasattr(bpy.types, menu) else ""


def find(context):
    """The picked object, or the nearest above it with a menu: a piece
    of a product (a corbel's body, a window's sash) shows the product."""
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    o = obj
    while o is not None:
        if menu_id(o):
            return o
        o = o.parent
    return None


# ---- Reading a menu ------------------------------------------------------------

class _OpProps:
    """What a menu's draw sets on an operator button."""

    def __init__(self):
        object.__setattr__(self, '_values', {})

    def __setattr__(self, name, value):
        self._values[name] = value

    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError(name)


class _Recorder:
    """A stand-in UILayout: records commands, submenus, separators and
    headings; anything else it is asked for is taken and ignored."""

    def __init__(self, out):
        object.__setattr__(self, '_out', out)

    def __setattr__(self, name, value):
        pass        # operator_context, enabled, scale_y ...

    def __getattr__(self, name):
        # row(), column(), box(), split(), template_*() ... : the same
        # recorder, so whatever is drawn into them is recorded too.
        return lambda *args, **kwargs: self

    def operator(self, op_id, text=None, **_kwargs):
        props = _OpProps()
        self._out.append(('op', text, op_id, props))
        return props

    def menu(self, menu, text=None, **_kwargs):
        self._out.append(('menu', text, menu))

    def operator_menu_enum(self, op_id, prop, text=None, **_kwargs):
        self._out.append(('enum', text, op_id, prop))

    def separator(self, *args, **kwargs):
        self._out.append(('sep',))

    def label(self, text="", **_kwargs):
        self._out.append(('label', text))

    def prop(self, *args, **kwargs):
        pass

    def popover(self, *args, **kwargs):
        pass


class _MenuSelf:
    """`self` for a menu's draw: the recorder as its layout, and the
    menu class's own attributes and methods."""

    def __init__(self, cls, layout):
        self._cls = cls
        self.layout = layout
        self.bl_label = getattr(cls, 'bl_label', "")

    def __getattr__(self, name):
        attr = getattr(self._cls, name)
        return attr.__get__(self) if hasattr(attr, '__get__') else attr


def _record(context, menu, depth=0):
    """[entries] the menu draws, or [] if its draw failed."""
    cls = getattr(bpy.types, menu, None)
    if cls is None or depth > 3:
        return []
    out = []
    try:
        poll = getattr(cls, 'poll', None)
        if poll is not None and not poll(context):
            return []
        cls.draw(_MenuSelf(cls, _Recorder(out)), context)
    except Exception as ex:
        print('Home Builder: reading %s failed: %s' % (menu, ex))
    return out


def _op_label(op_id):
    try:
        mod, name = op_id.split('.', 1)
        return getattr(getattr(bpy.ops, mod), name).get_rna_type().name
    except Exception:
        return op_id


def _enum_items(op_id, prop):
    try:
        mod, name = op_id.split('.', 1)
        rna = getattr(getattr(bpy.ops, mod), name).get_rna_type()
        return [(it.identifier, it.name) for it in rna.properties[prop].enum_items]
    except Exception:
        return []


def _menu_label(menu):
    cls = getattr(bpy.types, menu, None)
    return getattr(cls, 'bl_label', menu) if cls is not None else menu


def _list_entries(context, menu, depth=1):
    """A submenu as a pick list: (label, operator, kwargs), with a
    heading for each submenu inside it and a separator between groups."""
    out = []
    for rec in _record(context, menu, depth):
        if rec[0] == 'op':
            kwargs = dict(rec[3]._values)
            kwargs['INVOKE'] = True
            out.append((rec[1] or _op_label(rec[2]), rec[2], kwargs))
        elif rec[0] == 'enum':
            for ident, label in _enum_items(rec[2], rec[3]):
                out.append((label, rec[2], {rec[3]: ident, 'INVOKE': True}))
        elif rec[0] == 'menu':
            out.append((rec[1] or _menu_label(rec[2]), None, {}))
            out.extend(_list_entries(context, rec[2], depth + 1))
        elif rec[0] == 'sep':
            if out and out[-1][1] is not None:
                out.append(("", None, {}))
        elif rec[0] == 'label' and rec[1]:
            out.append((rec[1], None, {}))
    while out and out[-1][1] is None:
        out.pop()
    return out


def _opener(menu, label):
    """A button's callable that opens a submenu's commands as a list."""
    def entries(context, m=menu):
        return _list_entries(context, m)
    entries.__name__ = 'menu_' + label
    return entries


_cache = (None, 0.0, ())        # (key, time, blocks)
CACHE_SECONDS = 0.25


def command_blocks(context, menu):
    """The menu's commands as rows of buttons: two to a row, a new row
    after each separator."""
    global _cache
    obj = context.active_object
    key = (menu, obj.name if obj else "", len(context.selected_objects))
    if _cache[0] == key and time.monotonic() - _cache[1] < CACHE_SECONDS:
        return list(_cache[2])
    rows, row = [], []

    def flush():
        while row:
            rows.append(('actions', tuple(row[:2])))
            del row[:2]

    for rec in _record(context, menu):
        if rec[0] == 'op':
            row.append((rec[1] or _op_label(rec[2]), rec[2],
                        dict(rec[3]._values), None))
        elif rec[0] == 'enum':
            label = rec[1] or rec[3].replace('_', ' ').title()
            row.append((label + "…", _enum_opener(rec[2], rec[3]),
                        None, None))
        elif rec[0] == 'menu':
            label = rec[1] or _menu_label(rec[2])
            row.append((label + "…", _opener(rec[2], label), None, None))
        elif rec[0] == 'sep':
            flush()
    flush()
    _cache = (key, time.monotonic(), tuple(rows))
    return rows


def _enum_opener(op_id, prop):
    def entries(context):
        return [(label, op_id, {prop: ident, 'INVOKE': True})
                for ident, label in _enum_items(op_id, prop)]
    return entries


# ---- Prompts -------------------------------------------------------------------

PROMPT_TAG = 'HOME_BUILDER_PROP'
_prompt_schemas = {}    # key names -> schema key


def _ui(obj, key):
    try:
        return obj.id_properties_ui(key).as_dict()
    except Exception:
        return None


def prompt_keys(obj):
    """The custom properties `obj` declares as its prompts, in order."""
    out = []
    for key in obj.keys():
        ui = _ui(obj, key)
        if ui and ui.get('description') == PROMPT_TAG:
            out.append(key)
    return out


def _ident(key):
    return 'p_' + ''.join(c if c.isalnum() else '_' for c in key.lower())


def _prompt_prop(obj, key):
    from . import prop_proxy as P
    ui = _ui(obj, key) or {}
    value = obj.get(key)
    if ui.get('items'):
        return P.index_enum(key, [it[1] for it in ui['items']])
    if isinstance(value, bool) or isinstance(ui.get('default'), bool):
        return P.flag(key)
    if ui.get('subtype') == 'DISTANCE':
        return P.length(key)
    if ui.get('subtype') == 'ANGLE':
        return P.computed(lambda o, k=key: float(o.get(k, 0.0)),
                          lambda o, v, k=key: o.__setitem__(k, float(v)),
                          unit='ROTATION', precision=2)
    if isinstance(value, int):
        return P.number(key, hard_min=int(ui.get('min', 0)),
                        hard_max=int(ui.get('max', 10 ** 6)))
    if isinstance(value, float):
        return P.number(key, integer=False, hard_min=float(ui.get('min', -1e9)),
                        hard_max=float(ui.get('max', 1e9)))
    return None


def _solve(obj, context):
    from .. import hb_utils
    hb_utils.run_calc_fix(context, obj)


def prompt_owner(obj, exclude=()):
    """(owner, fields) for `obj`'s prompts, or (None, ()) when it has
    none. Objects with the same prompts share one schema. `exclude`
    names prompts that take more than a write (a page shows those its
    own way, or leaves them to the dialog)."""
    from . import prop_proxy
    keys = [k for k in prompt_keys(obj) if k not in exclude]
    if not keys:
        return None, ()
    props = {}
    fields = []
    for key in keys:
        prop = _prompt_prop(obj, key)
        if prop is None:
            continue
        ident = _ident(key)
        props[ident] = prop
        kind = {'ENUM': 'enum', 'BOOLEAN': 'bool'}.get(prop.type)
        if kind is None:
            kind = 'distance' if prop.unit == 'LENGTH' else 'number'
        fields.append((kind, ident, key))
    if not fields:
        return None, ()
    sig = tuple((f[1], props[f[1]].type, props[f[1]].unit,
                 tuple(i.name for i in props[f[1]].enum_items)) for f in fields)
    schema = _prompt_schemas.get(sig)
    if schema is None:
        schema = 'PROMPTS_%d' % len(_prompt_schemas)
        _prompt_schemas[sig] = schema
        prop_proxy.register(schema, props, after=_solve)
    return prop_proxy.owner(obj, schema), tuple(fields)


def prompt_blocks(context, obj, key, label="Prompts", open_first=True,
                  exclude=()):
    """A folding group of `obj`'s prompts, or [] when it has none."""
    from . import options_panel
    owner, fields = prompt_owner(obj, exclude)
    if owner is None:
        return []
    method = 'group:' + key
    if open_first and method not in _shown:
        _shown.add(method)
        if not options_panel.section_expanded(context, method):
            options_panel.toggle_section(context, method)
    return options_panel.field_blocks(context, (
        ('group', key, label, {'icon': 'settings', 'fields': fields}),
    ), owner)


_shown = set()


# ---- The page ----------------------------------------------------------------

def _size_text(context, obj):
    from .. import units
    from ..hb_types import GeoNodeObject
    try:
        node = GeoNodeObject(obj)
        if not all(node.has_input(n) for n in ('Dim X', 'Dim Y', 'Dim Z')):
            return None
        us = context.scene.unit_settings
        return "  x  ".join(units.unit_to_string(us, float(node.get_input(n)))
                            for n in ('Dim X', 'Dim Y', 'Dim Z'))
    except Exception:
        return None


def blocks(context, obj):
    # The picked piece's own commands where it has them, else the
    # product's.
    menu = menu_id(context.active_object) or menu_id(obj)
    out = [('head', (obj.name, False, None))]
    size = _size_text(context, obj)
    if size:
        out.append(('value', ("Size (W x D x H)", size)))
    out.extend(prompt_blocks(context, obj, 'generic_prompts'))
    out.append(('gap', None))
    out.extend(command_blocks(context, menu))
    return out
