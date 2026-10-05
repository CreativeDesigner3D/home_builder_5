"""Janela "Mover Sobre" (T026; D-15, RN-05 a RN-11, RF-28 a RF-33).

Painel desenhado sobre a viewport (`POST_PIXEL`) por um modal:
- vistas **Superior** (X × profundidade, frente embaixo) e **Frontal** (X × altura), só com A (laranja) e B (azul, a
  referência), no referencial de B;
- alvos: lados de B, linhas de profundidade (superior) e de altura (frontal) a 0/30/50/75/100%; clicar acima do topo
  de B na frontal empilha A; com uma parede como B, a linha da face da parede;
- distâncias de A a B (X, profundidade, altura) em campos digitáveis — clique no campo ou Tab, digite, Enter;
- Confirmar (Enter) grava como um passo de desfazer; Cancelar (Esc) devolve A à posição original;
- com "Evitar Sobreposição" ligado, o primeiro Confirmar avisa os módulos sobrepostos e o segundo confirma (RN-11).

Fora do painel, a navegação da viewport (botão do meio, roda) continua funcionando; os demais cliques são ignorados.
"""

import bpy  # type: ignore

from ..canvas2d import draw
from ..canvas2d.view import View2D
from ..data import units
from ..hb_gpu_draw import point_in_rect
from . import align
from .scene import MoveOver

NAV_EVENTS = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE',
              'NDOF_MOTION'}
FIELD_LABELS = ("X", "Profundidade", "Altura")
PCT = {0.0: "0%", 0.30: "30%", 0.50: "50%", 0.75: "75%", 1.0: "100%"}


def _scale():
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


class BTM_OT_MoveOverDialog(bpy.types.Operator):
    """Alinha o objeto arrastado ao objeto de referência pelas vistas superior e frontal"""
    bl_idname = "btm.move_over_dialog"
    bl_label = "Mover Sobre"
    bl_options = {'REGISTER', 'UNDO'}

    a_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    b_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    _handle = None

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    # Ciclo ------------------------------------------------------------------------------------------------
    def invoke(self, context, event):
        objects = context.scene.objects
        a, b = objects.get(self.a_name), objects.get(self.b_name)
        try:
            self.mo = MoveOver(context, a, b)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        self.mo.a.select_set(True)
        self.mo.b.select_set(True)
        context.view_layer.objects.active = self.mo.b          # B vira o ativo (RN-05)
        self.mo.preview()                                       # A assume a rotação de B (RN-08)
        self.hot = {'top': [], 'front': [], 'stack': False}
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.typing, self.buffer = None, ""
        self.warning, self.warned = "", False
        self.tolerance = context.window_manager.btm_move_over.tolerance_px
        self._layout(context)
        self._fit_views()
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "Mover Sobre  |  Clique perto de um lado ou de uma linha  |  Tab: digitar distância  |  "
            "Enter: confirmar  |  Esc: cancelar")
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        try:
            context.workspace.status_text_set(None)
        except (AttributeError, RuntimeError):
            pass
        if context.area:
            context.area.tag_redraw()

    def cancel(self, context):
        self.mo.restore()
        self._finish(context)

    # Geometria do painel ----------------------------------------------------------------------------------
    def _layout(self, context):
        s = _scale()
        region = context.region
        pad, pane_w, pane_h = 12 * s, 330 * s, 250 * s
        width = 3 * pad + 2 * pane_w
        height = pad * 6 + pane_h + 30 * s * 3
        x = max(pad, (region.width - width) / 2.0)
        y = max(pad, (region.height - height) / 2.0)
        self.panel = (x, y, width, height)
        top_y = y + height - pad - 22 * s - pane_h
        self.title_pos = (x + pad, y + height - pad - 14 * s)
        self.pane_top = (x + pad, top_y, pane_w, pane_h)
        self.pane_front = (x + 2 * pad + pane_w, top_y, pane_w, pane_h)
        row_y = top_y - pad - 26 * s
        field_w = (width - 2 * pad - 2 * pad) / 3.0
        self.fields = [(x + pad + i * (field_w + pad), row_y, field_w, 26 * s) for i in range(3)]
        self.warning_pos = (x + pad, row_y - pad - 14 * s)
        button_w, button_h = 120 * s, 28 * s
        self.button_ok = (x + width - pad - 2 * button_w - pad, y + pad, button_w, button_h)
        self.button_cancel = (x + width - pad - button_w, y + pad, button_w, button_h)

    def _fit_views(self):
        a, b = self.mo.box_a(), self.mo.box_b
        lo = [min(a[0][i], b[0][i]) for i in range(3)]
        hi = [max(a[1][i], b[1][i]) for i in range(3)]
        inset = 18 * _scale()

        def inner(rect):
            return (rect[0] + inset, rect[1] + inset, rect[2] - 2 * inset, rect[3] - 2 * inset - 14)

        self.view_top = View2D(inner(self.pane_top))
        self.view_top.fit(((lo[0], lo[1]), (hi[0], hi[1])), margin=0.15)
        self.view_front = View2D(inner(self.pane_front))
        self.view_front.fit(((lo[0], lo[2]), (hi[0], hi[2])), margin=0.15)

    # Alvos ------------------------------------------------------------------------------------------------
    def _lines_px(self, view, lines):
        return [(t, (view.to_screen(p0), view.to_screen(p1))) for t, (p0, p1) in lines]

    def _top_lines(self):
        return self._lines_px(self.view_top, align.top_view_lines(self.mo.box_b, self.mo.b_is_wall))

    def _front_lines(self):
        return self._lines_px(self.view_front, align.front_view_lines(self.mo.box_b))

    def _front_top_line_px(self):
        (bx0, _, _), (bx1, _, bz1) = self.mo.box_b
        return (self.view_front.to_screen((bx0, bz1)), self.view_front.to_screen((bx1, bz1)))

    def _hits(self, pixel):
        if point_in_rect(pixel[0], pixel[1], self.pane_top):
            return 'top', align.pick(pixel, self._top_lines(), self.tolerance), False
        if point_in_rect(pixel[0], pixel[1], self.pane_front):
            targets = align.pick(pixel, self._front_lines(), self.tolerance)
            stack = not targets and align.pick_stack(pixel, self._front_top_line_px(), self.tolerance)
            return 'front', targets, stack
        return None, [], False

    # Desenho ----------------------------------------------------------------------------------------------
    def _draw_pane(self, sh, rect, view, title, lines, hot, b_box2d, a_box2d, fraction_kind, stack_hot=False):
        draw.rect(sh, rect, draw.COLORS['pane'])
        draw.outline(sh, rect, draw.COLORS['border'])
        draw.text(rect[0] + 8, rect[1] + rect[3] - 18, title, draw.COLORS['muted'])
        draw.box(sh, view, b_box2d[0], b_box2d[1], draw.COLORS['reference'], fill=(0.25, 0.65, 1.0, 0.15))
        draw.box(sh, view, a_box2d[0], a_box2d[1], draw.COLORS['moving'], fill=(1.0, 0.62, 0.15, 0.12))
        for target, (p0, p1) in lines:
            is_hot = target in hot
            color = draw.COLORS['target_hot'] if is_hot else draw.COLORS['target']
            draw.lines(sh, [p0, p1] if is_hot else draw.dashed(p0, p1), color)
            if target.kind == fraction_kind and target.value in PCT:
                draw.text(max(p0[0], p1[0]) + 4, p0[1] - 4, PCT[target.value], color, size=10)
        if stack_hot:
            p0, p1 = self._front_top_line_px()
            draw.lines(sh, [p0, p1], draw.COLORS['target_hot'])
            draw.text((p0[0] + p1[0]) / 2 - 30, p0[1] + 6, "Empilhar", draw.COLORS['target_hot'])

    def _draw(self):
        sh = draw.begin()
        draw.rect(sh, self.panel, draw.COLORS['panel'])
        draw.outline(sh, self.panel, draw.COLORS['border'])
        draw.text(self.title_pos[0], self.title_pos[1],
                  f"Mover Sobre — {self.mo.a.name} sobre {self.mo.b.name} (referência)", size=13)
        a, b = self.mo.box_a(), self.mo.box_b
        self._draw_pane(sh, self.pane_top, self.view_top, "Superior (frente embaixo)", self._top_lines(),
                        self.hot['top'], ((b[0][0], b[0][1]), (b[1][0], b[1][1])),
                        ((a[0][0], a[0][1]), (a[1][0], a[1][1])), align.DEPTH)
        self._draw_pane(sh, self.pane_front, self.view_front, "Frontal", self._front_lines(),
                        self.hot['front'], ((b[0][0], b[0][2]), (b[1][0], b[1][2])),
                        ((a[0][0], a[0][2]), (a[1][0], a[1][2])), align.HEIGHT, self.hot['stack'])
        for i, rect in enumerate(self.fields):
            active = self.typing == i
            draw.rect(sh, rect, draw.COLORS['button_hot'] if active else draw.COLORS['button'])
            draw.outline(sh, rect, draw.COLORS['target_hot'] if active else draw.COLORS['border'])
            value = (self.buffer + "▏") if active else draw.length_label(self.mo.gaps()[i])
            draw.text(rect[0] + 8, rect[1] + 8, f"{FIELD_LABELS[i]}: {value}")
        if self.warning:
            draw.text(self.warning_pos[0], self.warning_pos[1], self.warning, draw.COLORS['warning'])
        draw.button(sh, self.button_ok, "Confirmar", hot=point_in_rect(*self.mouse, self.button_ok), primary=True)
        draw.button(sh, self.button_cancel, "Cancelar", hot=point_in_rect(*self.mouse, self.button_cancel))
        draw.end()

    # Ações ------------------------------------------------------------------------------------------------
    def _apply_click(self, pixel):
        pane, targets, stack = self._hits(pixel)
        if pane is None:
            return
        if stack:
            targets = [align.Target(align.STACK, None)]
        if targets:
            self.mo.align_to(targets)
            self.warned, self.warning = False, ""
            self._fit_views()

    def _commit_typing(self):
        try:
            value = units.parse_length(self.buffer, units.get_scene_length_unit(), allow_negative=True)
        except ValueError as exc:
            self.warning = str(exc)
            return False
        self.mo.set_gap(self.typing, value)
        self.typing, self.buffer = None, ""
        self.warned, self.warning = False, ""
        self._fit_views()
        return True

    def _confirm(self, context):
        settings = getattr(context.scene, 'btm_settings', None)
        if settings is not None and settings.collision_global and not self.warned:
            overlapping = self.mo.overlapping()
            if overlapping:
                names = ", ".join(o.name for o in overlapping[:4])
                self.warning = f"Sobrepõe: {names}. Confirme de novo para gravar mesmo assim."
                self.warned = True
                return {'RUNNING_MODAL'}
        self._finish(context)
        self.report({'INFO'}, f"{self.mo.a.name} alinhado a {self.mo.b.name}.")
        return {'FINISHED'}

    def modal(self, context, event):
        context.area.tag_redraw()
        pixel = (event.mouse_region_x, event.mouse_region_y)
        over_panel = point_in_rect(pixel[0], pixel[1], self.panel)
        if event.type in NAV_EVENTS and not over_panel:
            return {'PASS_THROUGH'}
        if event.type == 'MOUSEMOVE':
            self.mouse = pixel
            pane, targets, stack = self._hits(pixel)
            self.hot = {'top': targets if pane == 'top' else [], 'front': targets if pane == 'front' else [],
                        'stack': stack}
            return {'RUNNING_MODAL'}
        if self.typing is not None and event.value == 'PRESS':
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                self._commit_typing()
            elif event.type == 'ESC':
                self.typing, self.buffer = None, ""
            elif event.type == 'TAB':
                if self.buffer:
                    self._commit_typing()
                self.typing = 0 if self.typing is None else (self.typing + 1) % 3
            elif event.type == 'BACK_SPACE':
                self.buffer = self.buffer[:-1]
            elif event.unicode and event.unicode in "0123456789,.-mc ":
                self.buffer += event.unicode
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if point_in_rect(pixel[0], pixel[1], self.button_ok):
                return self._confirm(context)
            if point_in_rect(pixel[0], pixel[1], self.button_cancel):
                self.cancel(context)
                return {'CANCELLED'}
            for i, rect in enumerate(self.fields):
                if point_in_rect(pixel[0], pixel[1], rect):
                    self.typing, self.buffer = i, ""
                    return {'RUNNING_MODAL'}
            self._apply_click(pixel)
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS':
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                return self._confirm(context)
            if event.type in {'ESC', 'RIGHTMOUSE'}:
                self.cancel(context)
                return {'CANCELLED'}
            if event.type == 'TAB':
                self.typing, self.buffer = 0, ""
        return {'RUNNING_MODAL'}


classes = (BTM_OT_MoveOverDialog,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
