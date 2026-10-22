"""Annotation defaults that carry from one project to the next.

Set As Default in Dimension Options and "use for new text" in Line
Spacing save into the open file's scene, so every new project started
over from the stock values. These user-wide defaults live in a small
JSON file in Blender's user config folder instead: a project that has
not saved its own value falls back to them.
"""

import json
import os

import bpy

_FILE_NAME = 'hb5_annotation_defaults.json'


def _path():
    try:
        folder = bpy.utils.user_resource('CONFIG', create=True)
    except Exception:
        return None
    return os.path.join(folder, _FILE_NAME) if folder else None


def load():
    """The saved defaults as a dict ({} when none or unreadable)."""
    path = _path()
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save(**values):
    """Merge values into the saved defaults. Returns True when written."""
    path = _path()
    if not path:
        return False
    data = load()
    data.update(values)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except OSError:
        return False
    return True


def project_label():
    """What names the open project in a 'set in ...' note: its project
    number or name, else the file name ('' for an unsaved file)."""
    for scene in bpy.data.scenes:
        props = getattr(scene, 'hb_project', None)
        if props is None:
            continue
        for attr in ('project_number', 'project_name'):
            value = getattr(props, attr, '').strip()
            if value:
                return value
    return os.path.splitext(os.path.basename(bpy.data.filepath))[0]


def saved_from(key):
    """The project label stored with a default when it was saved."""
    return str(load().get(f'{key}_from', ''))


def _close(a, b):
    return abs(a - b) < 1e-5


def is_text_line_spacing(value):
    """True when value is the saved line spacing for new text."""
    return 'text_line_spacing' in load() and _close(value, text_line_spacing())


def is_additional_text_placement(x, y, size):
    """True when (x, y, size) is the saved additional text placement."""
    saved = additional_text_placement()
    return saved is not None and all(
        _close(a, b) for a, b in zip(saved, (x, y, size)))


def text_line_spacing():
    """Line spacing new annotation text starts with (1.0 = normal)."""
    try:
        value = float(load().get('text_line_spacing', 1.0))
    except (TypeError, ValueError):
        return 1.0
    return value if 0.1 <= value <= 5.0 else 1.0


def additional_text_placement():
    """(x, y, size) saved for a dimension's additional text, or None."""
    data = load()
    try:
        return (float(data['additional_text_x']),
                float(data['additional_text_y']),
                float(data['additional_text_size']))
    except (KeyError, TypeError, ValueError):
        return None
