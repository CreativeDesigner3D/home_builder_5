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
