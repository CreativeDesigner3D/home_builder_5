"""Style templates: the cabinet, door and drawer-front style pools saved
to a file in the user folder and loaded into another project.

A template is plain JSON holding every stored field of every style in
the three pools. Loading matches styles BY NAME: a style of the same
name is updated, a new one is added, and nothing already in the file
is removed (cabinets keep the style they are tagged with). One template
can be marked the default; a project whose style pools are still empty
starts from it instead of the built-in defaults (ensure_default_styles).
"""
import json
import os
import re

import bpy

FORMAT = "hb_face_frame_style_template"
VERSION = 1
_SETTINGS_FILE = "settings.json"

# Written first, in this order, so their update callbacks (which derive
# other fields) have settled before the stored values of those fields
# land. Same order the style copy operators use.
_CABINET_CASCADE = ('finish_color', 'finish_overlay', 'door_overlay_type')
_FRONT_CASCADE = ('front_series', 'front_shape', 'front_panel')

# Never stored: the style's own previous name (re-tags cabinets on a
# rename) and the finish materials each style builds for itself.
_SKIP = {'rna_type', 'rename_anchor', 'material', 'material_rotated',
         'interior_material', 'interior_material_rotated'}

# ID pointers are stored by name and resolved in the loading file.
_ID_COLLECTIONS = {'Material': 'materials', 'Object': 'objects'}


# ---------------------------------------------------------------------------
# Folder
# ---------------------------------------------------------------------------
def template_folder():
    return bpy.utils.extension_path_user(
        '.'.join(__package__.split('.')[:3]),
        path="style_templates", create=True)


def _safe_file_name(name):
    stem = re.sub(r'[<>:"/\\|?*]+', '_', name).strip(' .')
    return (stem or "Template") + ".json"


def template_path(name):
    return os.path.join(template_folder(), _safe_file_name(name))


def list_templates():
    """[(name, path)] sorted by name. The name is the one stored in the
    file, so a file renamed on disk still shows what it was saved as."""
    out = []
    try:
        folder = template_folder()
        files = os.listdir(folder)
    except Exception:
        return out
    for fn in files:
        if not fn.lower().endswith('.json') or fn == _SETTINGS_FILE:
            continue
        path = os.path.join(folder, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        if data.get('format') != FORMAT:
            continue
        out.append((data.get('name') or os.path.splitext(fn)[0], path))
    out.sort(key=lambda t: t[0].lower())
    return out


def find_template(name):
    for tname, path in list_templates():
        if tname == name:
            return path
    return None


def _read_settings():
    try:
        with open(os.path.join(template_folder(), _SETTINGS_FILE),
                  'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def get_default_template():
    """Name of the template new projects start from, or '' for none. A
    default whose file is gone reads as none."""
    name = _read_settings().get('default') or ''
    return name if name and find_template(name) else ''


def set_default_template(name):
    settings = _read_settings()
    settings['default'] = name or ''
    with open(os.path.join(template_folder(), _SETTINGS_FILE),
              'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=1)


# ---------------------------------------------------------------------------
# Dump
# ---------------------------------------------------------------------------
def _id_type(prop):
    fixed = getattr(prop, 'fixed_type', None)
    ident = getattr(fixed, 'identifier', '')
    return ident if ident in _ID_COLLECTIONS else None


def _is_id_pointer(prop):
    fixed = getattr(prop, 'fixed_type', None)
    cls = getattr(bpy.types, getattr(fixed, 'identifier', ''), None)
    try:
        return cls is not None and issubclass(cls, bpy.types.ID)
    except TypeError:
        return False


def _dump(pg):
    out = {}
    for prop in pg.bl_rna.properties:
        pid = prop.identifier
        if pid in _SKIP or prop.is_readonly and prop.type != 'COLLECTION' \
                and prop.type != 'POINTER':
            continue
        try:
            value = getattr(pg, pid)
        except Exception:
            continue
        if prop.type == 'COLLECTION':
            out[pid] = [_dump(item) for item in value]
        elif prop.type == 'POINTER':
            if _is_id_pointer(prop):
                if _id_type(prop) and value is not None:
                    out[pid] = {'__id__': value.name}
            elif value is not None:
                out[pid] = _dump(value)
        elif prop.type == 'ENUM' and prop.is_enum_flag:
            out[pid] = sorted(value)
        elif getattr(prop, 'is_array', False):
            out[pid] = list(value)
        else:
            out[pid] = value
    return out


def dump_styles(ff, name):
    return {
        'format': FORMAT,
        'version': VERSION,
        'name': name,
        'cabinet_styles': [_dump(s) for s in ff.cabinet_styles],
        'door_styles': [_dump(s) for s in ff.door_styles],
        'drawer_front_styles': [_dump(s) for s in ff.drawer_front_styles],
        'active_cabinet_style': _active_name(
            ff.cabinet_styles, ff.active_cabinet_style_index),
    }


def _active_name(coll, index):
    return coll[index].name if 0 <= index < len(coll) else ''


def save_template(ff, name):
    path = template_path(name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dump_styles(ff, name), f, indent=1)
    return path


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def _assign(pg, pid, value, skipped):
    prop = pg.bl_rna.properties.get(pid)
    if prop is None or pid in _SKIP:
        return
    try:
        if prop.type == 'COLLECTION':
            coll = getattr(pg, pid)
            coll.clear()
            for data in value or ():
                _load(coll.add(), data, skipped)
        elif prop.type == 'POINTER':
            if isinstance(value, dict) and '__id__' in value:
                kind = _id_type(prop)
                target = (getattr(bpy.data, _ID_COLLECTIONS[kind]).get(
                    value['__id__']) if kind else None)
                if target is None:
                    skipped.append("%s (%s not in this file)"
                                   % (pid, value['__id__']))
                    return
                setattr(pg, pid, target)
            elif isinstance(value, dict):
                _load(getattr(pg, pid), value, skipped)
        elif prop.is_readonly:
            return
        elif prop.type == 'ENUM' and prop.is_enum_flag:
            setattr(pg, pid, set(value or ()))
        else:
            setattr(pg, pid, value)
    except Exception as ex:
        # A value the running catalog no longer offers: keep going.
        skipped.append("%s=%r (%s)" % (pid, value, ex))


def _load(pg, data, skipped, first=(), skip=()):
    for pid in first:
        if pid in data:
            _assign(pg, pid, data[pid], skipped)
    for pid, value in data.items():
        if pid in first or pid in skip:
            continue
        _assign(pg, pid, value, skipped)


def _same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) < 1e-7
        except (TypeError, ValueError):
            return False
    if isinstance(a, (set, list, tuple)) or isinstance(b, (set, list, tuple)):
        try:
            if isinstance(a, set) or isinstance(b, set):
                return set(a) == set(b)
            return (len(a) == len(b)
                    and all(_same(x, y) for x, y in zip(a, b)))
        except TypeError:
            return False
    return a == b


def _drifted(pg, data):
    """Stored plain fields whose live value no longer matches the file."""
    out = []
    for pid, value in data.items():
        prop = pg.bl_rna.properties.get(pid)
        if (prop is None or pid in _SKIP or pid == 'name' or prop.is_readonly
                or prop.type in ('COLLECTION', 'POINTER')):
            continue
        try:
            if not _same(getattr(pg, pid), value):
                out.append(pid)
        except Exception:
            pass
    return out


def _settle(loaded, skipped, passes=3):
    """Put back stored values that a later write's callback re-derived.

    Update callbacks reach across fields and styles (an overlay rewrites
    the frame widths, a cabinet style's wood moves its door style onto
    that wood's default panel), so after the full load the file's values
    are written again wherever they drifted, until nothing moves."""
    for _ in range(passes):
        moved = False
        for pg, data in loaded:
            for pid in _drifted(pg, data):
                moved = True
                _assign(pg, pid, data[pid], [])
        if not moved:
            return
    for pg, data in loaded:
        for pid in _drifted(pg, data):
            skipped.append("%s on %s (kept %r)"
                           % (pid, pg.name, getattr(pg, pid)))


def _upsert(coll, name):
    for item in coll:
        if item.name == name:
            return item, False
    item = coll.add()
    item.name = name
    return item, True


def apply_template(context, data):
    """Load a template dict into the project's style pools. Returns
    (cabinet styles, door styles, drawer front styles, skipped values).

    Every write is held under suspend_propagate, then each loaded style
    is pushed to the cabinets / fronts that carry it once at the end, so
    a populated project is restyled once per style, not once per field.
    """
    from . import props_hb_face_frame as props
    from . import types_face_frame
    ff = props.get_style_props(context)
    skipped = []
    loaded_fronts = []
    loaded_cabinets = []
    loaded = []
    with props.suspend_propagate():
        for key in ('door_styles', 'drawer_front_styles'):
            pool = getattr(ff, key)
            for sdata in data.get(key) or ():
                name = sdata.get('name')
                if not name:
                    continue
                ds, _new = _upsert(pool, name)
                _load(ds, sdata, skipped, first=_FRONT_CASCADE,
                      skip=('name',))
                # The series / shape / panel pick renames a style whose
                # name is an automatic one; the template's name is what
                # the cabinet styles point at, so it is put back.
                if ds.name != name:
                    ds.name = name
                ds.rename_anchor = ds.name
                loaded_fronts.append(ds)
                loaded.append((ds, sdata))
        for sdata in data.get('cabinet_styles') or ():
            name = sdata.get('name')
            if not name:
                continue
            cs, _new = _upsert(ff.cabinet_styles, name)
            _load(cs, sdata, skipped, first=_CABINET_CASCADE,
                  skip=('name',))
            cs.rename_anchor = cs.name
            loaded_cabinets.append(cs)
            loaded.append((cs, sdata))
        _settle(loaded, skipped)
        # A settled series / panel pick can auto-rename a front style;
        # the template's names are what the cabinet styles point at.
        for pg, sdata in loaded:
            if pg.name != sdata['name']:
                pg.name = sdata['name']
                pg.rename_anchor = pg.name
        active = data.get('active_cabinet_style')
        for i, cs in enumerate(ff.cabinet_styles):
            if cs.name == active:
                ff.active_cabinet_style_index = i
                break
    with types_face_frame.suspend_recalc():
        for ds in loaded_fronts:
            try:
                props._propagate_door_style(ds, context)
            except Exception as ex:
                print("Home Builder: front style %r not applied: %s"
                      % (ds.name, ex))
        for cs in loaded_cabinets:
            try:
                props._propagate_cabinet_style(cs, context)
            except Exception as ex:
                print("Home Builder: cabinet style %r not applied: %s"
                      % (cs.name, ex))
    for line in skipped:
        print("Home Builder: style template skipped %s" % line)
    return len(loaded_cabinets), len(loaded_fronts), skipped


def read_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('format') != FORMAT:
        raise ValueError("not a style template")
    return data


def apply_default_template(context):
    """Load the default template, if one is set. Called when the style
    pools are empty; returns True when a template was applied."""
    name = get_default_template()
    if not name:
        return False
    try:
        apply_template(context, read_template(find_template(name)))
    except Exception as ex:
        print("Home Builder: default style template %r not loaded: %s"
              % (name, ex))
        return False
    return True
