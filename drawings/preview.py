"""Drawings preview: the room's sheets shown in a 3D viewport, read
straight from the model and kept in step with it.

The viewport it is started over shows a sheet instead of the model.
Split the area first and the model stays up beside it: the preview only
takes the events that happen over its own area, and it reads the model
again a moment after each change.

Everything is worked with the buttons on the sheet (hud.py): tabs for
the sheets, a bar for fit / refresh / print / close, and a toolbar over
the view that is clicked for its scale, its place and its sections.
Wheel zooms, middle drag pans, dragging a view moves it. The keys of the
first version still work (arrows, Home, R, P, [ ], X, T, Backspace).
"""

import os
import re
import tempfile
import time

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d

from . import gpu_painter, hud, sheets, views

DESK = (0.32, 0.33, 0.35, 1.0)
TICK = 0.3                  # seconds between looks at the model
MIN_TEXTURE, MAX_TEXTURE = 1.5, 4.0     # pixels to the point
QUIET_TICKS = 2             # ticks after a reading that changes are its own

_st = {}


def is_open():
    return bool(_st)


def _region(area):
    return next((r for r in area.regions if r.type == 'WINDOW'), None)


def _read(context, st):
    """Compose every sheet from the model as it stands."""
    started = time.perf_counter()
    names = []
    try:
        pages = sheets.compose_project(context)
        names = [(p.info or {}).get('name') or "Sheet" for p in pages]
        st['error'] = None
    except Exception as exc:
        import traceback
        traceback.print_exc()
        pages = []
        st['error'] = str(exc)
    st['names'] = names
    st['rooms'] = [(p.info or {}).get('room') or '' for p in pages]
    # A sheet that came back unchanged (its room did not change) keeps
    # its batches and its texture.
    before = {id(p): (c, st.get('tex', {}).get(i))
              for i, (p, c) in enumerate(zip(st.get('pages') or (),
                                             st.get('compiled') or ()))}
    kept_tex, compiled, fresh = {}, [], set()
    for i, page in enumerate(pages):
        old = before.pop(id(page), None)
        if old is None:
            compiled.append(gpu_painter.Compiled(page))
            fresh.add(i)
        else:
            compiled.append(old[0])
            if old[1] is not None:
                kept_tex[i] = old[1]
            else:
                fresh.add(i)
    for _comp, tex in before.values():
        if tex is not None:
            tex[0].free()
    st['tex'] = kept_tex
    st['pages'] = pages
    st['compiled'] = compiled
    st['placed'] = [list((p.info or {}).get('placed', ())) for p in pages]
    st['notes'] = [list((p.info or {}).get('notes', ())) for p in pages]
    st['page'] = min(st.get('page', 0), max(len(pages) - 1, 0))
    st['stale'] = fresh
    st['scene'] = context.scene.name
    st['gen'] = st['seen_gen'] = views.model_generation()
    # Reading the model stirs the dependency graph (a hidden part shown
    # while its shape is taken), and that can be reported a moment
    # later: for the next ticks a change is our own, not the user's,
    # so one reading can never set off the next.
    st['quiet'] = QUIET_TICKS
    st['note'] = f"read in {time.perf_counter() - started:.2f} s"


def _free(st, index=None):
    for i in list(st.get('tex', {})):
        if index is None or i == index:
            st['tex'].pop(i)[0].free()


def _fit(st, comp, region):
    """(pixels to the point the sheet shows at, pixels to the point its
    texture wants)."""
    fit = min((region.width - 40.0) / comp.width,
              (region.height - 60.0) / comp.height)
    f = max(fit * st['zoom'], 0.01)
    return f, min(max(f * 1.25, MIN_TEXTURE), MAX_TEXTURE)


def _paint(st, area):
    """Paint the sheet on show into its texture when it has none or its
    drawing changed. Called by the operator, between the viewport's
    draws; the texture already up stays until the new one is whole."""
    region = _region(area) if area is not None else None
    if region is None or not st.get('compiled'):
        return False
    i = st['page']
    if i not in st['stale'] and st['tex'].get(i) is not None:
        return False
    comp = st['compiled'][i]
    _f, want = _fit(st, comp, region)
    try:
        fresh = (gpu_painter.render(comp, want), want)
    except Exception as exc:
        st['stale'].discard(i)          # do not try every tick
        st['note'] = f"could not paint: {exc}"
        print("Drawings preview: paint:", exc)
        return False
    _free(st, i)
    st['tex'][i] = fresh
    st['stale'].discard(i)
    area.tag_redraw()
    return True


def _draw():
    st = _st
    area = bpy.context.area
    if not st or area is None or area.as_pointer() != st.get('area'):
        return
    region = bpy.context.region
    try:
        # Nothing is painted into a texture from here: that binds
        # another framebuffer in the middle of the viewport's own draw,
        # and the frame it happened in came out as the bare 3D view.
        # The operator paints (_paint); this only shows what is ready.
        if st['compiled']:
            i = st['page']
            comp = st['compiled'][i]
            f, st['want'] = _fit(st, comp, region)
        uni = gpu.shader.from_builtin('UNIFORM_COLOR')
        back = batch_for_shader(uni, 'TRI_FAN', {'pos': [
            (0, 0), (region.width, 0), (region.width, region.height),
            (0, region.height)]})
        gpu.state.blend_set('NONE')
        uni.bind()
        uni.uniform_float('color', DESK)
        back.draw(uni)
        blf.size(0, 12.0)
        blf.color(0, 1.0, 1.0, 1.0, 1.0)
        blf.position(0, 14.0, 12.0, 0.0)
        scene = page_scene(st)
        if not st['compiled']:
            blf.draw(0, "Drawings: " + (
                st.get('error') or "no wall with products in this room"))
            hud.draw(st, area, scene)
            return
        w, h = comp.width * f, comp.height * f
        x = (region.width - w) / 2.0 + st['pan'][0]
        y = (region.height - h) / 2.0 + st['pan'][1]
        st['rect'] = (x, y, f)
        if st['tex'].get(i) is None:
            blf.draw(0, "Drawings: preparing the sheet...")
            hud.draw(st, area, scene)
            return
        draw_texture_2d(st['tex'][i][0].texture_color, (x, y), w, h)
        move = st.get('move')
        if move and move.get('now'):
            # The view being dragged, as an outline where it will land.
            dx = move['now'][0] - move['start'][0]
            dy = move['now'][1] - move['start'][1]
            bx0, by0, bx1, by1 = move['box']
            ghost = batch_for_shader(uni, 'LINE_LOOP', {'pos': [
                (x + bx0 * f + dx, y + by0 * f + dy),
                (x + bx1 * f + dx, y + by0 * f + dy),
                (x + bx1 * f + dx, y + by1 * f + dy),
                (x + bx0 * f + dx, y + by1 * f + dy)]})
            uni.bind()
            uni.uniform_float('color', (0.1, 0.45, 0.95, 1.0))
            ghost.draw(uni)
        hud.draw(st, area, scene)
    except Exception as exc:        # never break the viewport
        if st.get('draw_error') != repr(exc):
            st['draw_error'] = repr(exc)
            print("Drawings preview:", exc)


def _pdf_path(context):
    if bpy.data.filepath:
        folder = os.path.dirname(bpy.data.filepath)
        name = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
    else:
        folder, name = tempfile.gettempdir(), context.scene.name
    stem = re.sub(r'[\\/:*?"<>|]+', '_', f"{name} - Drawings")
    return os.path.join(folder, stem + ".pdf")


def page_scene(st, context=None):
    """The room the sheet on show belongs to: what its edits are kept
    with, whichever room the model is showing."""
    rooms = st.get('rooms') or []
    name = rooms[st['page']] if st.get('page', 0) < len(rooms) else None
    scene = bpy.data.scenes.get(name) if name else None
    return scene or (context or bpy.context).scene


def _wall_cuts_shown(st, wall_name):
    """A wall's section cuts as they stand on the sheets."""
    return [it.get('x') or 0.0 for items in st.get('placed') or ()
            for it in items
            if it['kind'] == 'SECTION' and it.get('wall') == wall_name]


class HOME_BUILDER_OT_drawings_preview(bpy.types.Operator):
    """Show this room's drawing sheets in this viewport, read from the
    model as it stands"""
    bl_idname = 'home_builder.drawings_preview'
    bl_label = "Drawings Preview"

    def invoke(self, context, event):
        if is_open():
            _st['close'] = True
            return {'CANCELLED'}
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'ERROR'}, "Start it over a 3D viewport")
            return {'CANCELLED'}
        st = _st
        st.update(area=context.area.as_pointer(), tex={}, zoom=1.0,
                  pan=[0.0, 0.0], page=0, drag=None)
        _read(context, st)
        _paint(st, context.area)
        st['handle'] = bpy.types.SpaceView3D.draw_handler_add(
            _draw, (), 'WINDOW', 'POST_PIXEL')
        st['timer'] = context.window_manager.event_timer_add(
            TICK, window=context.window)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _close(self, context):
        st = _st
        if st.get('handle'):
            bpy.types.SpaceView3D.draw_handler_remove(st['handle'], 'WINDOW')
        if st.get('timer'):
            context.window_manager.event_timer_remove(st['timer'])
        _free(st)
        st.clear()
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}

    def _area(self, context):
        for area in context.window.screen.areas:
            if area.as_pointer() == _st.get('area'):
                return area
        return None

    def _hit(self, event, region):
        """The placed view under the cursor (the smallest, where they
        overlap) and the cursor in sheet points."""
        st = _st
        rect = st.get('rect')
        placed = st.get('placed') or []
        if not rect or st['page'] >= len(placed):
            return None, None
        x, y, f = rect
        sx = (event.mouse_x - region.x - x) / f
        sy = (event.mouse_y - region.y - y) / f
        best = None
        for item in placed[st['page']]:
            bx0, by0, bx1, by1 = item['box']
            if bx0 - 4 <= sx <= bx1 + 4 and by0 - 4 <= sy <= by1 + 4:
                area_ = (bx1 - bx0) * (by1 - by0)
                if best is None or area_ < best[0]:
                    best = (area_, item)
        return (best[1] if best else None), (sx, sy)

    def _hit_note(self, event, region):
        """(note, 'TIP' | 'TEXT') under the cursor, or (None, None)."""
        st = _st
        rect = st.get('rect')
        notes = st.get('notes') or []
        if not rect or st['page'] >= len(notes):
            return None, None
        x, y, f = rect
        sx = (event.mouse_x - region.x - x) / f
        sy = (event.mouse_y - region.y - y) / f
        reach = 5.0 / f
        sel = hud.selected_note(st)
        if sel is not None and sel.get('tip') and (
                abs(sx - sel['tip'][0]) <= reach
                and abs(sy - sel['tip'][1]) <= reach):
            return sel, 'TIP'
        for entry in notes[st['page']]:
            bx0, by0, bx1, by1 = entry['box']
            if bx0 - 2 <= sx <= bx1 + 2 and by0 - 2 <= sy <= by1 + 2:
                return entry, 'TEXT'
        return None, None

    def _sheet_point(self, event, region):
        x, y, f = _st['rect']
        return ((event.mouse_x - region.x - x) / f,
                (event.mouse_y - region.y - y) / f)

    def _change_note(self, context, entry, change, said):
        """Apply change(note) to one stored note (None removes it)."""
        scene = page_scene(_st, context)
        notes = sheets.view_notes(scene, entry['view'])
        if entry['index'] < len(notes):
            new = change(dict(notes[entry['index']]))
            if new is None:
                del notes[entry['index']]
                _st['note_sel'] = None
            else:
                notes[entry['index']] = new
        sheets.set_view_notes(scene, entry['view'], notes)
        self._edited(context, said)

    def _finish_typing(self, context, keep=True):
        st = _st
        typing = st.get('typing')
        st['typing'] = None
        if not typing:
            return
        text = typing['text'].strip()
        scene = page_scene(st, context)
        notes = sheets.view_notes(scene, typing['view'])
        index = typing['index']
        if not keep:
            return
        if index is None:
            if not text:
                return
            notes.append({'x': typing['x'], 'y': typing['y'], 'text': text,
                          'tip': None})
            st['note_sel'] = (typing['view']['key'], len(notes) - 1)
        elif index < len(notes):
            notes[index] = dict(notes[index], text=text)
            if not text:
                st['note_sel'] = None
        sheets.set_view_notes(scene, typing['view'], notes)
        self._edited(context, "note typed" if text else "note removed")

    def _type(self, context, event, area):
        """A key while a note is being typed."""
        st = _st
        typing = st['typing']
        kind = event.type
        if kind in ('RET', 'NUMPAD_ENTER'):
            if getattr(event, 'shift', False):
                typing['text'] += '\n'
            else:
                self._finish_typing(context)
        elif kind == 'ESC':
            self._finish_typing(context, keep=False)
        elif kind == 'BACK_SPACE':
            typing['text'] = typing['text'][:-1]
        else:
            char = getattr(event, 'unicode', '') or ''
            if char and char.isprintable():
                typing['text'] += char
        area.tag_redraw()

    def _edited(self, context, note):
        st = _st
        try:
            bpy.ops.ed.undo_push(message="Drawings: " + note)
        except Exception:
            pass
        _read(context, st)
        st['note'] = note
        # The selected view may have gone to another sheet: follow it.
        key = st.get('selected')
        if key:
            for i, items in enumerate(st.get('placed') or ()):
                if any(it['key'] == key for it in items):
                    st['page'] = i
                    break
            else:
                st['selected'] = None

    def _print(self, context):
        st = _st
        try:
            path = sheets.write_pdf(context, _pdf_path(context), st['pages'])
            st['note'] = "wrote " + path
            try:
                bpy.ops.wm.path_open(filepath=path)
            except Exception:
                pass
        except Exception as exc:
            st['note'] = f"PDF failed: {exc}"

    def _act(self, context, ident):
        """Do what the button `ident` is for. Returns a modal result
        when the preview closed, else None."""
        st = _st
        scene = page_scene(st, context)
        count = max(len(st['compiled']), 1)
        if isinstance(ident, tuple) and ident[0] == 'ROOM':
            rooms = st.get('rooms') or []
            if ident[1] in rooms:
                st['page'] = rooms.index(ident[1])
            return None
        if ident == 'PREV':
            st['page'] = (st['page'] - 1) % count
        elif ident == 'NEXT':
            st['page'] = (st['page'] + 1) % count
        elif isinstance(ident, tuple) and ident[0] == 'TAB':
            st['page'] = min(max(int(ident[1]), 0), count - 1)
        elif ident == 'FIT':
            st['zoom'], st['pan'] = 1.0, [0.0, 0.0]
        elif ident == 'REFRESH':
            _read(context, st)
        elif ident == 'PRINT':
            self._print(context)
        elif ident == 'RESET':
            sheets.reset_edits(scene)
            self._edited(context, "layout reset")
        elif ident == 'CLOSE':
            return self._close(context)
        else:
            item = hud.selected_item(st)
            if item is None:
                return None
            wall = bpy.data.objects.get(item.get('wall') or '')
            if ident in ('SCALE_DOWN', 'SCALE_UP') and item.get('n'):
                sheets.step_scale(scene, item['key'], item['n'],
                                  ident == 'SCALE_UP')
                self._edited(context, "scale changed")
            elif ident == 'HOME':
                sheets.home_view(scene, item['key'])
                self._edited(context, "view put back")
            elif ident == 'ADD_CUT':
                st['pick'] = None if st.get('pick') else 'CUT'
            elif ident == 'REMOVE' and wall is not None:
                sheets.remove_cut(scene, wall, item.get('x') or 0.0,
                                  _wall_cuts_shown(st, wall.name))
                st['selected'] = None
                self._edited(context, "section removed")
            elif ident == 'TOGETHER' and item.get('wall'):
                sheets.toggle_together(scene, item['wall'])
                self._edited(context, "sections moved")
            elif ident == 'ADD_NOTE':
                st['pick'] = None if st.get('pick') == 'NOTE' else 'NOTE'
        return None

    def _act_note(self, context, ident):
        st = _st
        entry = hud.selected_note(st)
        if entry is None:
            return
        if ident == 'NOTE_EDIT':
            n = (entry['at'][0] - entry['origin'][0]) / entry['k']
            st['typing'] = {'view': entry['view'], 'index': entry['index'],
                            'text': entry.get('text', ''), 'at': entry['at'],
                            'x': n, 'y': 0.0}
        elif ident == 'NOTE_LEADER':
            if entry.get('tip'):
                self._change_note(context, entry,
                                  lambda n: dict(n, tip=None),
                                  "leader removed")
            else:
                st['pick'] = None if st.get('pick') == 'TIP' else 'TIP'
        elif ident == 'NOTE_REMOVE':
            self._change_note(context, entry, lambda n: None, "note removed")

    def _tick(self, context, area):
        """Follow the model: read it again once it has stopped changing
        and nothing else is in the middle of an action."""
        st = _st
        gen = views.model_generation()
        if st.get('quiet', 0) > 0:
            st['quiet'] -= 1
            st['gen'] = st['seen_gen'] = gen
        if context.scene.name != st['scene']:
            # The model went to another room: show that room's sheets.
            st['scene'] = context.scene.name
            rooms = st.get('rooms') or []
            if st['scene'] in rooms and not st.get('move'):
                st['page'] = rooms.index(st['scene'])
                st['selected'] = None
                area.tag_redraw()
        changed = gen != st['gen']
        settled = gen == st.get('seen_gen')
        st['seen_gen'] = gen
        busy = len(context.window.modal_operators) > 1
        if changed and settled and not busy and not st['drag'] \
                and not st.get('move'):
            _read(context, st)
            area.tag_redraw()
            return
        # A sheet zoomed well past its texture is painted again, sharp.
        have = st['tex'].get(st['page'])
        want = st.get('want')
        settled = time.perf_counter() - st.get('zoomed', 0.0) > 0.4
        if have and want and not st['drag'] and settled and (
                abs(want - have[1]) / have[1] > 0.3):
            st['stale'].add(st['page'])
            area.tag_redraw()

    def modal(self, context, event):
        result = self._handle(context, event)
        if _st:
            # Whatever the event changed (the sheet on show, its
            # drawing, the zoom) is painted here, between draws.
            try:
                _paint(_st, self._area(context))
            except Exception as exc:
                print("Drawings preview: paint:", exc)
        return result

    def _handle(self, context, event):
        st = _st
        if not st:
            return {'CANCELLED'}
        area = self._area(context)
        if area is None or st.get('close'):
            return self._close(context)
        if event.type == 'TIMER':
            self._tick(context, area)
            return {'PASS_THROUGH'}
        region = _region(area)
        over = (region is not None
                and region.x <= event.mouse_x < region.x + region.width
                and region.y <= event.mouse_y < region.y + region.height)
        if st['drag'] and event.type == 'MOUSEMOVE':
            st['pan'][0] += event.mouse_x - st['drag'][0]
            st['pan'][1] += event.mouse_y - st['drag'][1]
            st['drag'] = (event.mouse_x, event.mouse_y)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if st['drag'] and event.type == 'MIDDLEMOUSE' \
                and event.value == 'RELEASE':
            st['drag'] = None
            return {'RUNNING_MODAL'}
        if st.get('typing'):
            # Every key goes to the note; a click anywhere finishes it.
            if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
                              'WINDOW_DEACTIVATE'):
                return {'PASS_THROUGH'}
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self._finish_typing(context)
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.value == 'PRESS':
                self._type(context, event, area)
            return {'RUNNING_MODAL'}
        move = st.get('move')
        if move and event.type == 'MOUSEMOVE':
            move['now'] = (event.mouse_x, event.mouse_y)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if move and event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            st['move'] = None
            now = move.get('now') or move['start']
            f = (st.get('rect') or (0, 0, 1.0))[2]
            dx = (now[0] - move['start'][0]) / f
            dy = (now[1] - move['start'][1]) / f
            entry = move.get('note')
            if entry is not None:
                # A note's text, or the tip of its leader, dragged.
                if abs(dx) > 1.0 or abs(dy) > 1.0:
                    mx_, my_ = dx / entry['k'], dy / entry['k']
                    if move['part'] == 'TIP':
                        self._change_note(
                            context, entry, lambda n: dict(
                                n, tip=[n['tip'][0] + mx_, n['tip'][1] + my_]
                                if n.get('tip') else None), "leader moved")
                    else:
                        self._change_note(
                            context, entry, lambda n: dict(
                                n, x=n['x'] + mx_, y=n['y'] + my_),
                            "note moved")
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            if abs(dx) > 1.0 or abs(dy) > 1.0:
                sheets.move_view(page_scene(st, context), move['key'],
                                 dx, dy)
                self._edited(context, "view moved")
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if not over:
            if st.get('hover') or st.get('hover_view'):
                st['hover'] = st['hover_view'] = None
                area.tag_redraw()
            return {'PASS_THROUGH'}
        press = event.value == 'PRESS'
        scene = page_scene(st, context)
        mx, my = event.mouse_x - region.x, event.mouse_y - region.y
        button = hud.hit(st, area, scene, mx, my)
        if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'):
            # What is under the cursor lights up: a button, or a view.
            under = None
            if button is None:
                item, _at = self._hit(event, region)
                under = item['key'] if item else None
            if button != st.get('hover') or under != st.get('hover_view'):
                st['hover'], st['hover_view'] = button, under
                area.tag_redraw()
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and press:
            if button is not None:
                if isinstance(button, str) and button.startswith('NOTE_'):
                    self._act_note(context, button)
                elif button != 'LABEL':
                    closed = self._act(context, button)
                    if closed is not None:
                        return closed
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            if st.get('pick') == 'TIP' and st.get('rect'):
                # Where the selected note's leader should point.
                st['pick'] = None
                entry = hud.selected_note(st)
                if entry is not None:
                    px, py = self._sheet_point(event, region)
                    tip = [(px - entry['origin'][0]) / entry['k'],
                           (py - entry['origin'][1]) / entry['k']]
                    self._change_note(context, entry,
                                      lambda n: dict(n, tip=tip),
                                      "leader added")
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            if st.get('pick') == 'NOTE' and st.get('rect'):
                # Where a new note should stand, then it is typed.
                st['pick'] = None
                view = hud.selected_item(st)
                if view is not None:
                    px, py = self._sheet_point(event, region)
                    st['typing'] = {
                        'view': {'kind': view['kind'], 'wall': view['wall'],
                                 'key': view['key']},
                        'index': None, 'text': '', 'at': (px, py),
                        'x': (px - view['origin'][0]) / view['k'],
                        'y': (py - view['origin'][1]) / view['k']}
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            entry, part = self._hit_note(event, region)
            if entry is not None:
                # A click selects the note; a drag moves it or its tip.
                st['note_sel'] = (entry['view']['key'], entry['index'])
                st['selected'] = None
                tip = entry.get('tip')
                box = ((tip[0] - 3, tip[1] - 3, tip[0] + 3, tip[1] + 3)
                       if part == 'TIP' else entry['box'])
                st['move'] = {'note': entry, 'part': part, 'box': box,
                              'start': (event.mouse_x, event.mouse_y)}
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            st['note_sel'] = None
            item, at = self._hit(event, region)
            cutting = st.get('pick') == 'CUT' or event.ctrl
            st['pick'] = None
            if item and cutting and item['kind'] == 'ELEVATION' \
                    and item.get('origin') and item.get('k'):
                wall = bpy.data.objects.get(item['wall'] or '')
                x_cut = (at[0] - item['origin'][0]) / item['k']
                if wall is not None and x_cut > 0.0:
                    sheets.add_cut(scene, wall, round(x_cut, 4),
                                   _wall_cuts_shown(st, wall.name))
                    self._edited(context, "section added")
            elif item and item.get('key'):
                # A click selects the view; a drag from it moves it.
                st['selected'] = item['key']
                st['move'] = {'key': item['key'], 'box': item['box'],
                              'start': (event.mouse_x, event.mouse_y)}
            else:
                st['selected'] = None
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if press and event.type in ('LEFT_BRACKET', 'RIGHT_BRACKET', 'X',
                                    'DEL', 'T', 'BACK_SPACE'):
            item, _at = self._hit(event, region)
            if event.type == 'BACK_SPACE':
                sheets.reset_edits(scene)
                self._edited(context, "set back to the rule")
            elif item is None:
                pass
            elif event.type in ('LEFT_BRACKET', 'RIGHT_BRACKET'):
                if item.get('key') and item.get('n'):
                    n = sheets.step_scale(scene, item['key'], item['n'],
                                          event.type == 'RIGHT_BRACKET')
                    self._edited(context, "scale 1:%d" % n)
            elif event.type in ('X', 'DEL'):
                wall = bpy.data.objects.get(item.get('wall') or '')
                if item['kind'] == 'SECTION' and wall is not None:
                    sheets.remove_cut(scene, wall, item.get('x') or 0.0,
                                      _wall_cuts_shown(st, wall.name))
                    self._edited(context, "section removed")
            elif event.type == 'T' and item.get('wall'):
                sheets.toggle_together(scene, item['wall'])
                self._edited(context, "sections moved")
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        count = max(len(st['compiled']), 1)
        if event.type == 'ESC' and press:
            # Esc backs out one step at a time.
            if st.get('pick'):
                st['pick'] = None
            elif st.get('note_sel'):
                st['note_sel'] = None
            elif st.get('selected'):
                st['selected'] = None
            else:
                return self._close(context)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if press and event.type in ('RIGHT_ARROW', 'PAGE_DOWN'):
            st['page'] = (st['page'] + 1) % count
        elif press and event.type in ('LEFT_ARROW', 'PAGE_UP'):
            st['page'] = (st['page'] - 1) % count
        elif event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE'):
            k = 1.2 if event.type == 'WHEELUPMOUSE' else 1 / 1.2
            new = min(max(st['zoom'] * k, 0.5), 12.0)
            k = new / st['zoom']
            # The point under the cursor stays where it is.
            cx = event.mouse_x - region.x - region.width / 2.0
            cy = event.mouse_y - region.y - region.height / 2.0
            st['pan'][0] = cx - (cx - st['pan'][0]) * k
            st['pan'][1] = cy - (cy - st['pan'][1]) * k
            st['zoom'] = new
            st['zoomed'] = time.perf_counter()
        elif event.type == 'MIDDLEMOUSE' and press:
            st['drag'] = (event.mouse_x, event.mouse_y)
        elif event.type == 'HOME' and press:
            st['zoom'], st['pan'] = 1.0, [0.0, 0.0]
        elif event.type == 'R' and press:
            _read(context, st)
        elif event.type == 'P' and press:
            self._print(context)
        elif event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER',
                            'WINDOW_DEACTIVATE'):
            return {'PASS_THROUGH'}
        # Everything else over the sheet is swallowed: there is no model
        # under it to click on.
        area.tag_redraw()
        return {'RUNNING_MODAL'}


def _menu(self, context):
    # Still being built: only offered with Developer Extras on.
    if context.preferences.view.show_developer_ui:
        self.layout.separator()
        self.layout.operator(
            HOME_BUILDER_OT_drawings_preview.bl_idname,
            text="Close Drawings Preview" if is_open()
            else "Drawings Preview")


def register():
    bpy.utils.register_class(HOME_BUILDER_OT_drawings_preview)
    bpy.types.VIEW3D_MT_view.append(_menu)


def unregister():
    if _st.get('handle'):
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_st['handle'], 'WINDOW')
        except Exception:
            pass
    _st.clear()
    bpy.types.VIEW3D_MT_view.remove(_menu)
    bpy.utils.unregister_class(HOME_BUILDER_OT_drawings_preview)
