"""View kinds: each turns a piece of the model into a Drawing.

A view is a plain dict -- {'kind': 'ELEVATION', 'wall': 'Wall.001'} --
and its resolver reads the model and returns a Drawing in the view's
own paper space. A resolver never knows the sheet it will sit on, never
draws its own title, and never changes the model.

Drawings are cached until the model changes, so a sheet that is looked
at again, or two sheets that show the same wall, cost one reading.
"""

import json

import bpy

from ..operators import elevation_mode as em
from .drawing import Drawing

HALF_INCH_SCALE = 72.0 / 0.0254 / 24.0      # points to the metre, 1/2" = 1'
INCH_SCALE = 72.0 / 0.0254 / 12.0           # 1" = 1'

_kinds = {}
_cache = {}
_model_gen = 0
_reading = 0


def register_view_kind(kind, resolver):
    """resolver(context, view, width, height) -> Drawing, or None when
    the view has nothing to show. `width` x `height` is the room on the
    sheet the view may fill."""
    _kinds[kind] = resolver
    _cache.clear()


def unregister_view_kind(kind):
    _kinds.pop(kind, None)
    _cache.clear()


def model_generation():
    """Rises whenever the model changes: what a cached drawing is good
    until."""
    return _model_gen


class reading:
    """`with reading():` -- the model is only being read. A reader may
    still stir the dependency graph (a hidden part shown while its shape
    is taken, then hidden again); that is not a change to the model."""

    def __enter__(self):
        global _reading
        _reading += 1

    def __exit__(self, *_exc):
        global _reading
        _reading -= 1
        return False


@bpy.app.handlers.persistent
def _on_change(*_args):
    global _model_gen
    if not _reading:
        _model_gen += 1


@bpy.app.handlers.persistent
def _on_load(*_args):
    global _model_gen
    _model_gen += 1
    _cache.clear()


def resolve(context, view, width, height):
    """The Drawing of `view`, read from the model or from the cache."""
    resolver = _kinds.get(view.get('kind'))
    if resolver is None:
        return None
    settings = {k: v for k, v in view.items() if not k.startswith('_')}
    key = (context.scene.name, _model_gen,
           json.dumps(settings, sort_keys=True, default=str),
           round(width), round(height))
    hit = _cache.get(key)
    if hit is not None:
        return hit
    with reading():
        drawing = resolver(context, view, width, height)
    if len(_cache) > 200:
        _cache.clear()
    # Stale generations are dropped as new ones arrive.
    for old in [k for k in _cache if k[0] == key[0] and k[1] != key[1]]:
        del _cache[old]
    _cache[key] = drawing
    return drawing


def wall_of(view):
    wall = bpy.data.objects.get(view.get('wall') or '')
    if wall is None or em._frame(wall) is None:
        return None
    return wall


def wall_items(scene, wall):
    return em._items(scene, wall, em._front_names(scene, wall), ())


# What a sheet's elevation leaves to the sheet: the plan and the iso are
# views of their own there, and detail cards are placed by the sheet.
ELEVATION_SHOWS = {'PLAN': False, 'ISO': False, 'DETAILS': False}


def _elevation(context, view, width, height):
    """The wall's elevation exactly as the Elevation View prints it:
    line work, rule-placed dimensions, notes."""
    wall = wall_of(view)
    if wall is None:
        return None
    drawing = Drawing(width, height)
    info = {}
    with em.show_overrides(ELEVATION_SHOWS):
        em.draw_wall(drawing, context, wall, width, height, title=False,
                     info=info)
    k = info['k']
    drawing.anchors['wall_start'] = (info['ox'], info['oy'])
    drawing.anchors['wall_top'] = (info['ox'],
                                   info['oy'] + info['height'] * k)
    drawing.info = {'k': k, 'scale': info['label']}
    return drawing


def register():
    from . import plan, section
    register_view_kind('ELEVATION', _elevation)
    register_view_kind('PLAN', plan.resolve)
    register_view_kind('ROOM_PLAN', plan.resolve_room)
    register_view_kind('SECTION', section.resolve)
    handlers = bpy.app.handlers
    if _on_change not in handlers.depsgraph_update_post:
        handlers.depsgraph_update_post.append(_on_change)
    if _on_load not in handlers.load_post:
        handlers.load_post.append(_on_load)


def unregister():
    handlers = bpy.app.handlers
    if _on_change in handlers.depsgraph_update_post:
        handlers.depsgraph_update_post.remove(_on_change)
    if _on_load in handlers.load_post:
        handlers.load_post.remove(_on_load)
    _kinds.clear()
    _cache.clear()
