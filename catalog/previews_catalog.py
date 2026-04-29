"""Preview-icon collection for catalog thumbnails.

Wraps bpy.utils.previews to provide stable icon_id values that
template_list / layout.label can render via icon_value=.

Right now there's only one preview - no_thumbnail.png - which is the
fallback shown for any item that doesn't have a real thumbnail yet.
When per-item thumbnails ship, this module gains a load step (or a
"Render Library Thumbnails" command populates it) and get_icon_id
returns the matching id.
"""
import os
import bpy
import bpy.utils.previews


_pcoll = None
_PLACEHOLDER_KEY = '__no_thumbnail__'


def _thumbs_dir():
    return os.path.join(os.path.dirname(__file__), 'thumbnails')


def _placeholder_path():
    return os.path.join(_thumbs_dir(), 'no_thumbnail.png')


def get_icon_id(thumbnail_filename='', item_id=''):
    """Return a Blender icon_id for the given thumbnail.

    Resolution order:
      1) `thumbnail_filename` if non-empty and the file exists
         (explicit override on the catalog entry).
      2) `{item_id}.png` - the convention used by the renderer.
      3) The placeholder (no_thumbnail.png).

    Lazily loads files into the previews collection on first
    reference, so we don't pay disk cost for thumbnails the user
    never views.
    """
    if _pcoll is None:
        return 0  # not registered yet - safe fallback (no icon)

    candidates = []
    if thumbnail_filename:
        candidates.append(thumbnail_filename)
    if item_id:
        candidates.append(f"{item_id}.png")

    for fname in candidates:
        if fname in _pcoll:
            return _pcoll[fname].icon_id
        full = os.path.join(_thumbs_dir(), fname)
        if os.path.isfile(full):
            try:
                _pcoll.load(fname, full, 'IMAGE')
                return _pcoll[fname].icon_id
            except Exception:
                pass  # fall through

    if _PLACEHOLDER_KEY in _pcoll:
        return _pcoll[_PLACEHOLDER_KEY].icon_id
    return 0


def reload():
    """Drop and re-create the preview collection.

    Called after rendering thumbnails so freshly-saved PNGs are
    picked up on the next panel draw. Also tags every UI area for
    redraw so the new icon_ids resolve immediately without manual
    refresh.
    """
    global _pcoll
    if _pcoll is not None:
        try:
            bpy.utils.previews.remove(_pcoll)
        except Exception:
            pass
        _pcoll = None
    _pcoll = bpy.utils.previews.new()
    placeholder = _placeholder_path()
    if os.path.isfile(placeholder):
        try:
            _pcoll.load(_PLACEHOLDER_KEY, placeholder, 'IMAGE')
        except Exception:
            pass
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def register():
    global _pcoll
    if _pcoll is not None:
        # Already registered - reload placeholder to reflect any png changes
        try:
            bpy.utils.previews.remove(_pcoll)
        except Exception:
            pass
        _pcoll = None

    _pcoll = bpy.utils.previews.new()
    placeholder = _placeholder_path()
    if os.path.isfile(placeholder):
        _pcoll.load(_PLACEHOLDER_KEY, placeholder, 'IMAGE')
    # If the placeholder file is missing the collection still exists
    # and get_icon_id falls back to 0 (no icon shown).


def unregister():
    global _pcoll
    if _pcoll is not None:
        try:
            bpy.utils.previews.remove(_pcoll)
        except Exception:
            pass
        _pcoll = None
