"""Settings that are not properties, made to read like them.

The Options-tab field engine (``options_panel``) reads and writes a
field with getattr / setattr on an owner, and asks the owner's RNA what
the value is: a length, an angle, a count, one of a list. Many products
keep their settings elsewhere -- an object's custom properties
("Toe Kick Height"), its geometry-node inputs ("Dim X"), its height off
the floor -- where no getattr reaches.

A schema names those settings once, each with how to read and write it
and what kind of value it is; ``owner(obj, key)`` is then an owner the
engine takes like any property group. A write runs the schema's
``after`` -- the solve the product's own dialog would have run -- so the
model follows the field as it changes.
"""
import bpy


PATH_PREFIX = '#proxy:'

_schemas = {}           # key -> (props {name: Prop}, after(obj, context))


class _Item:
    __slots__ = ('identifier', 'name', 'description')

    def __init__(self, identifier, name):
        self.identifier = identifier
        self.name = name
        self.description = ""


class Prop:
    """One setting: how to read it, how to write it, and what it is, as
    RNA would say (type, unit, precision, range, enum items)."""

    def __init__(self, get, set=None, type='FLOAT', unit='NONE',
                 precision=3, hard_min=-1e9, hard_max=1e9, items=()):
        self.get = get
        self.set = set
        self.type = type
        self.unit = unit
        self.subtype = 'DISTANCE' if unit == 'LENGTH' else 'NONE'
        self.precision = precision
        self.hard_min = hard_min
        self.hard_max = hard_max
        self.is_readonly = set is None
        self.enum_items = [_Item(i, n) for i, n in items]


class _RNA:
    """Enough of bl_rna for the field engine: ``properties[name]``."""

    def __init__(self, props):
        self.properties = props


# ---- Building a schema -------------------------------------------------------

def _id_get(key, default, cast):
    def get(obj):
        try:
            return cast(obj.get(key, default))
        except (TypeError, ValueError):
            return default
    return get


def _id_set(key, cast):
    def set(obj, value):
        obj[key] = cast(value)
    return set


def length(key, default=0.0):
    """A custom property holding a distance."""
    return Prop(_id_get(key, default, float), _id_set(key, float),
                unit='LENGTH', precision=4, hard_min=0.0)


def number(key, default=0, integer=True, hard_min=0, hard_max=1e9):
    cast = int if integer else float
    return Prop(_id_get(key, default, cast), _id_set(key, cast),
                type='INT' if integer else 'FLOAT',
                hard_min=hard_min, hard_max=hard_max)


def flag(key, default=False):
    """A custom property holding a checkbox."""
    return Prop(_id_get(key, default, bool), _id_set(key, bool),
                type='BOOLEAN')


def index_enum(key, labels, default=0):
    """A custom property holding an index into `labels` (a COMBOBOX
    prompt), shown as one of a list."""
    def get(obj):
        try:
            return str(int(obj.get(key, default)))
        except (TypeError, ValueError):
            return str(default)

    def set(obj, value):
        obj[key] = int(value)
    return Prop(get, set, type='ENUM',
                items=[(str(i), label) for i, label in enumerate(labels)])


def node_input(name, unit='LENGTH'):
    """A geometry-node input on the object's own modifier."""
    from ..hb_types import GeoNodeObject

    def get(obj):
        try:
            return float(GeoNodeObject(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        GeoNodeObject(obj).set_input(name, float(value))
    return Prop(get, set, unit=unit, precision=4, hard_min=0.0)


def computed(get, set=None, type='FLOAT', unit='NONE', items=(), **kw):
    """A setting worked out from the object: get(obj), set(obj, value)."""
    return Prop(get, set, type=type, unit=unit, items=items, **kw)


def height_off_floor():
    """The object's world height, moved by the difference so it keeps
    its place under a parent."""
    def get(obj):
        return float(obj.matrix_world.translation.z)

    def set(obj, value):
        dz = float(value) - obj.matrix_world.translation.z
        if abs(dz) > 1e-7:
            obj.location.z += dz
            bpy.context.view_layer.update()
    return Prop(get, set, unit='LENGTH', precision=4)


# ---- Registry ----------------------------------------------------------------

def register(key, props, after=None):
    """Name a schema: {field name: Prop}, and what runs after a write."""
    _schemas[key] = (dict(props), after)


def unregister(key):
    _schemas.pop(key, None)


class Owner:
    """An object seen through a schema."""

    __slots__ = ('_obj', '_key')

    def __init__(self, obj, key):
        object.__setattr__(self, '_obj', obj)
        object.__setattr__(self, '_key', key)

    @property
    def id_data(self):
        return self._obj

    @property
    def bl_rna(self):
        return _RNA(_schemas[self._key][0])

    @property
    def name(self):
        return self._obj.name

    def path_from_id(self):
        return PATH_PREFIX + self._key

    def has(self, prop):
        return prop in _schemas.get(self._key, ({}, None))[0]

    def __getattr__(self, prop):
        props = _schemas.get(self._key, ({}, None))[0]
        p = props.get(prop)
        if p is None:
            raise AttributeError(prop)
        return p.get(self._obj)

    def __setattr__(self, prop, value):
        props, after = _schemas[self._key]
        p = props.get(prop)
        if p is None or p.set is None:
            raise AttributeError("%s cannot be set" % prop)
        p.set(self._obj, value)
        if after is not None:
            try:
                after(self._obj, bpy.context)
            except Exception as ex:
                print('Home Builder: updating %s failed: %s'
                      % (self._obj.name, ex))

    def __eq__(self, other):
        return (isinstance(other, Owner) and other._obj == self._obj
                and other._key == self._key)

    def __hash__(self):
        return hash((self._obj.name, self._key))


def owner(obj, key):
    return Owner(obj, key)


def resolve(id_data, path):
    """The owner a field key's (ID, path) names, for one built here."""
    return Owner(id_data, path[len(PATH_PREFIX):])
