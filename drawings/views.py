"""View kinds: each turns a piece of the model into a Drawing.

A view is a plain dict -- {'kind': 'ELEVATION', 'wall': 'Wall.001'} --
and its resolver reads the model and returns a Drawing in the view's
own paper space. A resolver never knows the sheet it will sit on, never
draws its own title, and never changes the model.

Drawings are cached until the model changes, so a sheet that is looked
at again, or two sheets that show the same wall, cost one reading.
"""

import contextlib
import json

import bpy

from ..operators import elevation_mode as em
from .drawing import Drawing

HALF_INCH_SCALE = 72.0 / 0.0254 / 24.0      # points to the metre, 1/2" = 1'
INCH_SCALE = 72.0 / 0.0254 / 12.0           # 1" = 1'

_kinds = {}
_cache = {}
_model_gen = 0
_scene_gens = {}            # scene name -> how often that room changed
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


def model_generation(scene=None):
    """Rises whenever the model changes: what a cached drawing is good
    until. With a scene, only that room's changes count, so a change in
    one room leaves the drawings of the others good."""
    if scene is None:
        return _model_gen
    return _scene_gens.get(scene.name, 0)


def touch(scene):
    """Say that a room changed in a way the dependency graph does not
    report (something kept in a custom property)."""
    global _model_gen
    _model_gen += 1
    _scene_gens[scene.name] = _scene_gens.get(scene.name, 0) + 1


def _project_generation(scene):
    """A room's own changes and those of the scene that holds what the
    whole project shares (its styles)."""
    from .. import hb_project
    try:
        main = hb_project.get_main_scene()
    except Exception:
        main = None
    own = _scene_gens.get(scene.name, 0)
    if main is None or main == scene:
        return (own,)
    return (own, _scene_gens.get(main.name, 0))


@contextlib.contextmanager
def showing_cages(rooms):
    """A room that is not on screen keeps its products' cages switched
    off, and nothing switched off is measured: show them while the
    rooms are read, and put them back after."""
    hidden = []
    with reading():
        for room in rooms:
            for obj in room.objects:
                if obj.get('IS_GEONODE_CAGE') and obj.hide_viewport:
                    obj.hide_viewport = False
                    hidden.append(obj)
        if hidden:
            for room in rooms:
                try:
                    room.view_layers[0].update()
                except Exception:
                    pass
            em._bump_gen()
        try:
            yield
        finally:
            for obj in hidden:
                try:
                    obj.hide_viewport = True
                except ReferenceError:
                    pass
            layers = {room.view_layers[0] for room in rooms
                      if room.view_layers}
            for layer in layers:
                try:
                    layer.update()
                except Exception:
                    pass
            em._bump_gen()


@contextlib.contextmanager
def in_room(context, room):
    """A context whose scene is `room`, whichever room is on screen."""
    if context.scene == room:
        yield context
        return
    layer = room.view_layers[0]
    with context.temp_override(scene=room, view_layer=layer):
        with reading():
            layer.update()
        em._bump_gen()
        try:
            yield bpy.context
        finally:
            em._bump_gen()


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
def _on_change(scene=None, *_args):
    global _model_gen
    if not _reading:
        _model_gen += 1
        name = getattr(scene, 'name', None)
        if name:
            _scene_gens[name] = _scene_gens.get(name, 0) + 1


@bpy.app.handlers.persistent
def _on_load(*_args):
    global _model_gen
    _model_gen += 1
    _scene_gens.clear()
    _cache.clear()


def resolve(context, view, width, height):
    """The Drawing of `view`, read from the model or from the cache."""
    resolver = _kinds.get(view.get('kind'))
    if resolver is None:
        return None
    settings = {k: v for k, v in view.items() if not k.startswith('_')}
    key = (context.scene.name, _project_generation(context.scene),
           json.dumps(settings, sort_keys=True, default=str),
           round(width), round(height))
    hit = _cache.get(key)
    if hit is not None:
        return hit
    with reading():
        drawing = resolver(context, view, width, height)
        # Settle what the reading stirred while it still counts as a
        # reading, so it is not taken for a change to the model later.
        try:
            context.view_layer.update()
        except Exception:
            pass
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
ELEVATION_SHOWS = {'PLAN': False, 'ISO': False, 'DETAILS': False,
                   # The units' number tags another add-on hangs on the
                   # wall: the sheet sets its own, sized to fit.
                   'UNIT_TAGS': False}


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
                     info=info, scale=view.get('scale'))
    k = info['k']
    try:
        _elevation_marks(drawing, context, wall, k, info['ox'],
                         info['oy'])
    except Exception as exc:
        print(f"Drawings: elevation marks: {exc}")
    drawing.anchors['wall_start'] = (info['ox'], info['oy'])
    drawing.anchors['wall_top'] = (info['ox'],
                                   info['oy'] + info['height'] * k)
    drawing.info = {'k': k, 'scale': info['label']}
    return drawing


# ---- What a sheet's elevation adds to the print ------------------------------
#
# Drafting marks placed by rule from the parts themselves: each unit's
# number in a tag sized to fit it, the lines that show which side a
# door is hinged, and a label on each adjustable shelf.

DOOR_HINGE = {'LEFT_DOOR': -1, 'RIGHT_DOOR': 1}
SHELF_ROLES = ('SHELF', 'ADJUSTABLE_SHELF')
TAG_SIZE, TAG_MIN_SIZE = 5.5, 4.0


def unit_number(obj):
    """The number a unit is known by on the drawings and the parts
    lists, or None: whatever a numbering add-on stamped on it."""
    for key in obj.keys():
        if key.endswith('UNIT_NUMBER') and obj.get(key):
            return str(obj[key])
    return None


def number_tag(page, cx, cy, text, room=None, size=TAG_SIZE):
    """A unit's number in a box centred on (cx, cy), set smaller when
    `room` (the width there is for it) is tight."""
    from .. import hb_pdf
    from . import draft
    if room is not None:
        while size > TAG_MIN_SIZE and (
                hb_pdf.text_width(text, size) + 5.0 > room):
            size -= 0.5
    w = hb_pdf.text_width(text, size) + 5.0
    h = size + 2.4
    page.fill_color(draft.WHITE)
    page.stroke_color(draft.INK)
    page.line_width(0.4)
    page.rect(cx - w / 2, cy - h / 2, w, h, fill=True, stroke=True)
    draft.text_centered(page, cx, cy - size * 0.36, text, size, halo=False)
    return w, h


def _elevation_marks(drawing, context, wall, k, ox, oy):
    from mathutils import Vector
    from . import draft
    scene = context.scene
    Fi = em._frame(wall)[1]
    deps = context.evaluated_depsgraph_get()

    def P(x, z):
        return (ox + x * k, oy + z * k)

    hinge_lines, shelf_labels, tags = [], [], []
    for it in wall_items(scene, wall):
        if it.kind == 'OPENING' or it.obj.get('IS_APPLIANCE'):
            continue
        for part in it.obj.children_recursive:
            role = part.get('hb_part_role')
            if part.type != 'MESH' or part.hide_render or (
                    role not in DOOR_HINGE and role not in SHELF_ROLES):
                continue
            ev = part.evaluated_get(deps)
            if ev.data is None or not len(ev.data.vertices):
                continue
            pts = [Fi @ (ev.matrix_world @ Vector(c)) for c in ev.bound_box]
            x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
            z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
            if role in DOOR_HINGE:
                side = DOOR_HINGE[role]
                hinge, free = (x0, x1) if side < 0 else (x1, x0)
                mid = P(hinge, (z0 + z1) / 2.0)
                hinge_lines += [(P(free, z0), mid), (mid, P(free, z1))]
            else:
                if z1 - z0 < 1.5 * 0.0254:
                    boards = [z1]
                else:
                    zs = sorted({round((Fi @ (ev.matrix_world @ v.co)).z, 4)
                                 for v in ev.data.vertices})
                    boards = [b for a, b in zip(zs[::2], zs[1::2])
                              if b - a < 1.5 * 0.0254]
                for z in boards:
                    shelf_labels.append(P((x0 + x1) / 2.0, z))
        number = unit_number(it.obj)
        if number:
            # Low on what stands on the floor (in its kick), high on
            # what hangs: clear of the fronts' own marks either way.
            z = it.z0 if it.kind == 'LOWER' else it.z1
            cx, cy = P((it.x0 + it.x1) / 2.0, z)
            cy += 6.0 if it.kind == 'LOWER' else -7.0
            tags.append((cx, cy, number, (it.x1 - it.x0) * k - 3.0))
    if hinge_lines:
        drawing.stroke_color(draft.GREY)
        drawing.line_width(0.3)
        drawing.dash(7.0, 2.0)
        drawing.lines(hinge_lines)
        drawing.dash()
    for cx, cy in shelf_labels:
        draft.text_centered(drawing, cx, cy + 2.0, 'ADJ', 5.0)
    for cx, cy, number, room in tags:
        number_tag(drawing, cx, cy, number, room)


def _details(context, view, _width, height):
    """The wall's detail cards (a moulding's section, a toe kick, an
    appliance panel) in a column, or columns when they do not stand in
    `height`: the cards the elevation shows beside the wall, as the
    Elevation View prints them. None when the wall has none, or the
    elevation's Details are switched off."""
    wall = wall_of(view)
    if wall is None:
        return None
    saved = em._print_scale
    em._print_scale = em.PRINT_TEXT_SCALE
    try:
        s = em._s()
        cards = em._cards(context.scene, wall)
        if not cards:
            return None
        limit = height if height > 1.0 else 1e9
        flow, total = em._cards_flow(cards, 0.0, limit, s)
        tall = max(y + h for _c, _x, y, _k, _w, h in flow)
        drawing = Drawing(total, tall)
        for card, cx, cy, k, w, h in flow:
            ox, oy = cx, tall - cy - h
            lines, texts, masks = {}, [], []
            for pr in card.get('prims', ()):
                kind = pr.get('kind')
                if kind == 'LINES':
                    width = max(em.CARD_MIN_LINE * s,
                                pr.get('width', 0.0) * k)
                    width = round(width * 4.0) / 4.0
                    lines.setdefault(width, []).extend(
                        (ox + p[0] * k, oy + p[1] * k)
                        for p in pr.get('points', ()))
                elif kind == 'TEXT':
                    rows, mask = em._card_text(context.scene, pr, ox, oy,
                                               k, w)
                    texts += rows
                    if mask is not None:
                        masks.append(mask)
            em._print_cards(drawing, {'cards': [{
                'rect': (ox, oy, w, h), 'lines': lines, 'texts': texts,
                'masks': masks}]})
    finally:
        em._print_scale = saved
    drawing.info = {'k': None}
    return drawing


def register():
    from . import iso, plan, section
    register_view_kind('ELEVATION', _elevation)
    register_view_kind('DETAILS', _details)
    iso.register()
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
