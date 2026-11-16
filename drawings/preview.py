"""Drawings preview: the room's sheets shown in a 3D viewport, read
straight from the model and kept in step with it.

The viewport it is started over shows a sheet instead of the model.
Split the area first and the model stays up beside it: the preview only
takes the events that happen over its own area, and it reads the model
again a moment after each change.

Over the preview: Left / Right = sheet, wheel = zoom, middle drag =
pan, Home = fit, R = read again, P = write the PDF, Esc = close.
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

from . import gpu_painter, sheets, views

DESK = (0.32, 0.33, 0.35, 1.0)
TICK = 0.3                  # seconds between looks at the model
MIN_TEXTURE, MAX_TEXTURE = 1.5, 4.0     # pixels to the point

_st = {}


def is_open():
    return bool(_st)


def _region(area):
    return next((r for r in area.regions if r.type == 'WINDOW'), None)


def _read(context, st):
    """Compose every sheet from the model as it stands."""
    started = time.perf_counter()
    try:
        pages = sheets.compose_all(context)
        st['error'] = None
    except Exception as exc:
        import traceback
        traceback.print_exc()
        pages = []
        st['error'] = str(exc)
    st['pages'] = pages
    st['compiled'] = [gpu_painter.Compiled(p) for p in pages]
    st['page'] = min(st.get('page', 0), max(len(pages) - 1, 0))
    st['stale'] = set(range(len(pages)))
    st['scene'] = context.scene.name
    st['gen'] = st['seen_gen'] = views.model_generation()
    st['note'] = f"read in {time.perf_counter() - started:.2f} s"


def _free(st, index=None):
    for i in list(st.get('tex', {})):
        if index is None or i == index:
            st['tex'].pop(i)[0].free()


def _draw():
    st = _st
    area = bpy.context.area
    if not st or area is None or area.as_pointer() != st.get('area'):
        return
    region = bpy.context.region
    try:
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
        if not st['compiled']:
            blf.draw(0, "Drawings: " + (
                st.get('error') or "no wall with products in this room")
                + "   |   Esc: close")
            return
        i = st['page']
        comp = st['compiled'][i]
        fit = min((region.width - 40.0) / comp.width,
                  (region.height - 60.0) / comp.height)
        f = max(fit * st['zoom'], 0.01)
        want = min(max(f * 1.25, MIN_TEXTURE), MAX_TEXTURE)
        have = st['tex'].get(i)
        if i in st['stale'] or have is None:
            _free(st, i)
            st['tex'][i] = (gpu_painter.render(comp, want), want)
            st['stale'].discard(i)
        st['want'] = want
        w, h = comp.width * f, comp.height * f
        x = (region.width - w) / 2.0 + st['pan'][0]
        y = (region.height - h) / 2.0 + st['pan'][1]
        draw_texture_2d(st['tex'][i][0].texture_color, (x, y), w, h)
        blf.draw(0, "Sheet %d of %d   |   Left / Right: sheet   wheel: zoom   "
                    "middle drag: pan   Home: fit   R: read again   P: PDF   "
                    "Esc: close   (%s)" % (i + 1, len(st['compiled']),
                                           st.get('note', '')))
    except Exception as exc:        # never break the viewport
        if st.get('draw_error') != repr(exc):
            st['draw_error'] = repr(exc)
            print("Drawings preview:", exc)


def _pdf_path(context):
    stem = re.sub(r'[\\/:*?"<>|]+', '_', f"{context.scene.name} - Drawings")
    folder = (os.path.dirname(bpy.data.filepath) if bpy.data.filepath
              else tempfile.gettempdir())
    return os.path.join(folder, stem + ".pdf")


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

    def _tick(self, context, area):
        """Follow the model: read it again once it has stopped changing
        and nothing else is in the middle of an action."""
        st = _st
        gen = views.model_generation()
        changed = gen != st['gen'] or context.scene.name != st['scene']
        settled = gen == st.get('seen_gen')
        st['seen_gen'] = gen
        busy = len(context.window.modal_operators) > 1
        if changed and settled and not busy and not st['drag']:
            _read(context, st)
            area.tag_redraw()
            return
        # A sheet zoomed well past its texture is painted again, sharp.
        have = st['tex'].get(st['page'])
        want = st.get('want')
        if have and want and not st['drag'] and (
                abs(want - have[1]) / have[1] > 0.3):
            st['stale'].add(st['page'])
            area.tag_redraw()

    def modal(self, context, event):
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
        if not over:
            return {'PASS_THROUGH'}
        press = event.value == 'PRESS'
        count = max(len(st['compiled']), 1)
        if event.type == 'ESC' and press:
            return self._close(context)
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
        elif event.type == 'MIDDLEMOUSE' and press:
            st['drag'] = (event.mouse_x, event.mouse_y)
        elif event.type == 'HOME' and press:
            st['zoom'], st['pan'] = 1.0, [0.0, 0.0]
        elif event.type == 'R' and press:
            _read(context, st)
        elif event.type == 'P' and press:
            try:
                path = sheets.write_pdf(context, _pdf_path(context),
                                        st['pages'])
                st['note'] = "wrote " + path
            except Exception as exc:
                st['note'] = f"PDF failed: {exc}"
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
