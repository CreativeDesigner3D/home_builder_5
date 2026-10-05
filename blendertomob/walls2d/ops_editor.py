"""Editor de Paredes: desenho da planta, ferramentas e OK/Cancelar (T029; RN-15 a RN-17, RF-01 a RF-09).

- `btm.wall_editor`: lê as paredes do ambiente (rascunho), abre a janela do editor e inicia o modal.
- `btm.wall_editor_modal`: recebe os eventos da tela 2D:
  - Selecionar/Mover: clicar numa linha seleciona o trecho e a face (interna/externa); arrastar um vértice com prévia,
    trava ortogonal (±2,5°), grade magnética e "Bloquear Ângulo";
  - Construir Parede (lápis): clique no ponto inicial, digite o comprimento e Enter (ou clique), trava ortogonal,
    clique no ponto inicial pergunta se deve fechar;
  - Inverter Sentido, Adicionar Vértice e Remover Vértice por clique; Delete remove o trecho selecionado;
  - botão do meio arrasta a vista, a roda aproxima, Home enquadra tudo.
- `btm.wall_editor_ok` / `btm.wall_editor_cancel`: o OK aplica o rascunho como um passo de desfazer (avisa antes se
  algum item não couber); Cancelar ou Esc descarta.
"""

import math

import bpy  # type: ignore

from ..canvas2d import draw
from ..canvas2d.view import View2D, distance_point_point, distance_point_segment, ortho_snap, snap_to_grid
from ..data import units
from . import model, props, window

NODE_HIT_PX = 9
LINE_HIT_PX = 7
SNAP_CLOSE_PX = 15          # ímã do ponto inicial, em pixels de tela (D-33)
CLOSE_TOLERANCE = 0.01      # fim a até 10 mm do início conta como chegar nele (D-34)
TIMER_STEP = 0.1

COLORS = {
    'background': (0.12, 0.12, 0.13, 1.0),
    'grid': (1.0, 1.0, 1.0, 0.06),
    'grid_axis': (1.0, 1.0, 1.0, 0.14),
    'wall': (0.85, 0.85, 0.88, 1.0),
    'wall_fill': (0.55, 0.55, 0.6, 0.18),
    'selected': (1.0, 0.62, 0.15, 1.0),
    'node': (0.25, 0.6, 1.0, 1.0),
    'preview': (0.35, 1.0, 0.45, 1.0),
    'preview_locked': (0.8, 0.8, 0.8, 1.0),
    'reference': (0.7, 0.7, 0.75, 0.55),
}


def _state(context):
    return context.window_manager.btm_wall_editor


def _region_rect(region, area=None):
    width = window.visible_width(area, region) if area is not None else float(region.width)
    return (0.0, 0.0, width, float(region.height))


def ensure_view(region, area=None):
    s = props.session()
    if s.view is None:
        s.view = View2D(_region_rect(region, area))
        s.view.fit(s.plan.bounds(), margin=0.15)
    else:
        s.view.rect = _region_rect(region, area)
    return s.view


# Desenho --------------------------------------------------------------------------------------------------

def draw_plan(context):
    s = props.session()
    region = context.region
    if s is None or region is None:
        return
    view = ensure_view(region, context.area)
    state = _state(context)
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), COLORS['background'])
    xs, ys = view.grid_lines(state.grid_size)
    grid = []
    for x in xs:
        grid += [view.to_screen((x, ys[0] if ys else 0)), view.to_screen((x, ys[-1] if ys else 0))]
    for y in ys:
        grid += [view.to_screen((xs[0] if xs else 0, y)), view.to_screen((xs[-1] if xs else 0, y))]
    draw.lines(sh, grid, COLORS['grid'])

    reference = []                        # paredes da camada nova: só para ver (D-05)
    for a, b in s.plan.references:
        reference += draw.dashed(view.to_screen(a), view.to_screen(b))
    if reference:
        draw.lines(sh, reference, COLORS['reference'])

    selected_chain, selected_index = s.segment()
    for ci, chain in enumerate(s.plan.chains):
        for i in range(chain.segment_count()):
            inner = chain.inner_line(i)
            outer = chain.outer_line(i)
            is_selected = chain is selected_chain and i == selected_index
            a0, a1 = view.to_screen(inner[0]), view.to_screen(inner[1])
            b0, b1 = view.to_screen(outer[0]), view.to_screen(outer[1])
            # Face interna tracejada (medida real), externa e pontas contínuas (D-28).
            draw.lines(sh, draw.dashed(a0, a1) + [b0, b1, a0, b0, a1, b1], COLORS['wall'])
            if is_selected:
                line = chain.line(i, s.line)
                a, b = view.to_screen(line[0]), view.to_screen(line[1])
                draw.lines(sh, [a, b, (a[0], a[1] + 1), (b[0], b[1] + 1)], COLORS['selected'])
                _draw_arrow(sh, view, chain, i)
            mid = ((inner[0][0] + inner[1][0]) / 2, (inner[0][1] + inner[1][1]) / 2)
            p = view.to_screen(mid)
            label = draw.length_label(chain.face_length(i, s.line if is_selected else model.INNER))
            draw.text(p[0] + 4, p[1] + 4, label, COLORS['selected'] if is_selected else draw.COLORS['muted'],
                      size=11)
        for k, node in enumerate(chain.nodes):
            q = view.to_screen(node)
            color = COLORS['selected'] if s.selected_node == (ci, k) else COLORS['node']
            draw.rect(sh, (q[0] - 4, q[1] - 4, 8, 8), color)

    if s.drawing is None and s.typed and s.cursor is not None:      # digitação direta (D-27)
        q = view.to_screen(s.cursor)
        draw.text(q[0] + 12, q[1] + 12, f"Medida: {s.typed}▏  (Enter aplica, Esc limpa)", COLORS['selected'])

    if s.drawing is not None and s.cursor is not None and s.drawing.nodes:
        start = s.drawing.nodes[-1]
        snapped = close_snap(s, view, view.to_screen(s.cursor))
        end, locked = (s.drawing.nodes[0], True) if snapped else preview_point(context, start, s.cursor)
        a, b = view.to_screen(start), view.to_screen(end)
        draw.lines(sh, [a, b] if locked else draw.dashed(a, b), COLORS['preview_locked'] if locked
                   else COLORS['preview'])
        if snapped:                                    # ímã: anel no ponto inicial e "Fechar" (D-33)
            ring = [(b[0] + 11 * math.cos(t * math.pi / 8), b[1] + 11 * math.sin(t * math.pi / 8)) for t in range(17)]
            draw.lines(sh, [p for k in range(16) for p in (ring[k], ring[k + 1])], COLORS['selected'])
            draw.text(b[0] + 14, b[1] - 18, "Fechar", COLORS['selected'])
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        text = f"{s.typed}▏" if s.typed else draw.length_label(length)
        draw.text(b[0] + 10, b[1] + 10, f"Comprimento: {text}", COLORS['preview'])

    hint = {'SELECT': "Clique numa face (interna tracejada / externa) ou num vértice e digite a medida + Enter; arraste "
                      "os vértices. Delete remove o trecho.",
            'DRAW': "Clique o ponto inicial, digite o comprimento e Enter. Clique no início para fechar. Esc termina.",
            'INVERT': "Clique numa parede para inverter o sentido.",
            'ADD_NODE': "Clique num trecho para dividi-lo.",
            'REMOVE_NODE': "Clique num vértice para unir os trechos."}[state.tool]
    draw.text(12, 12, hint, draw.COLORS['muted'])
    if s.error:
        draw.text(12, 32, s.error, draw.COLORS['warning'])
    if s.prompt in PROMPTS:
        _draw_prompt(sh, region, PROMPTS[s.prompt])
    draw.end()


def _draw_arrow(sh, view, chain, i):
    (x0, y0), (x1, y1) = chain.inner_line(i)
    mid = view.to_screen(((x0 + x1) / 2, (y0 + y1) / 2))
    d = chain.direction(i)
    ux, uy = math.cos(d), math.sin(d)
    tip = (mid[0] + ux * 18, mid[1] + uy * 18)
    left = (tip[0] - ux * 8 - uy * 5, tip[1] - uy * 8 + ux * 5)
    right = (tip[0] - ux * 8 + uy * 5, tip[1] - uy * 8 - ux * 5)
    draw.lines(sh, [mid, tip, tip, left, tip, right], COLORS['selected'])


PROMPT_W, PROMPT_H = 380, 90
PROMPTS = {'close': "Deseja fechar a parede e finalizar a sua construção?",
           'close_existing': "Deseja fechar a parede? O último ponto chegou ao início.",
           'discard': "Descartar as alterações e fechar o editor?"}


def _prompt_rects(region):
    x = (region.width - PROMPT_W) / 2
    y = (region.height - PROMPT_H) / 2
    return (x, y, PROMPT_W, PROMPT_H), (x + 60, y + 12, 100, 26), (x + 200, y + 12, 100, 26)


def _draw_prompt(sh, region, message):
    box, yes, no = _prompt_rects(region)
    draw.rect(sh, box, draw.COLORS['panel'])
    draw.outline(sh, box, draw.COLORS['border'])
    draw.text(box[0] + 16, box[1] + box[3] - 28, message)
    draw.button(sh, yes, "Sim", primary=True)
    draw.button(sh, no, "Não")


# Geometria da interação ----------------------------------------------------------------------------------------

def preview_point(context, start, cursor):
    point, locked = ortho_snap(start, cursor)
    state = _state(context)
    if state.magnetic and not locked:
        point = snap_to_grid(point, state.grid_size)
    return point, locked


def hit_node(s, pixel):
    for ci, chain in enumerate(s.plan.chains):
        for k, node in enumerate(chain.nodes):
            if distance_point_point(pixel, s.view.to_screen(node)) <= NODE_HIT_PX:
                return ci, k
    return None


def close_snap(s, view, pixel):
    """O cursor está no ímã do ponto inicial do desenho a lápis (2+ trechos, até 15 px)?"""
    d = s.drawing
    return (d is not None and d.segment_count() >= 2
            and distance_point_point(pixel, view.to_screen(d.nodes[0])) <= SNAP_CLOSE_PX)


def hit_line(s, pixel):
    """(cadeia, trecho, linha) mais próximo do clique."""
    best = None
    for ci, chain in enumerate(s.plan.chains):
        for i in range(chain.segment_count()):
            for line, which in ((chain.inner_line(i), model.INNER), (chain.outer_line(i), model.OUTER)):
                dist = distance_point_segment(pixel, s.view.to_screen(line[0]), s.view.to_screen(line[1]))
                if dist <= LINE_HIT_PX and (best is None or dist < best[0]):
                    best = (dist, ci, i, which)
    return None if best is None else best[1:]


def remove_segment(s, ci, i):
    """Remove o trecho `i` da cadeia `ci` (abre o contorno ou divide a cadeia aberta)."""
    chain = s.plan.chains[ci]
    seg = chain.segments[i]
    if seg.source:
        s.plan.removed_sources.append(seg.source)
    n = len(chain.nodes)
    if chain.closed:
        order = [(i + 1 + k) % n for k in range(n)]
        nodes = [chain.nodes[k] for k in order]
        segments = [chain.segments[(i + 1 + k) % n] for k in range(n - 1)]
        s.plan.chains[ci] = model.Chain(nodes, segments, False, chain.side)
        return
    left = model.Chain(chain.nodes[:i + 1], chain.segments[:i], False, chain.side)
    right = model.Chain(chain.nodes[i + 1:], chain.segments[i + 1:], False, chain.side)
    parts = [c for c in (left, right) if c.segment_count() > 0]
    s.plan.chains[ci:ci + 1] = parts   # a primeira parede da direita fica solta no OK (aplicador)
    s.selected = None


# Operadores -----------------------------------------------------------------------------------------------

class BTM_OT_WallEditor(bpy.types.Operator):
    """Abre o Editor de Paredes: planta 2D para desenhar e editar as paredes do ambiente"""
    bl_idname = "btm.wall_editor"
    bl_label = "Editar Paredes…"
    bl_options = {'REGISTER'}

    other_walls: bpy.props.EnumProperty(
        name="Paredes selecionadas de outra camada",
        items=[('CONVERT', "Converter para paredes editáveis",
                "Viram trechos editáveis; no OK, são trocadas por paredes do Home Builder 5"),
               ('REFERENCE', "Só referência", "Aparecem tracejadas na planta, sem edição")],
        default='CONVERT')  # type: ignore

    @classmethod
    def poll(cls, context):
        return not bpy.app.background and context.window is not None and props.session() is None

    def _other_layer(self, context):
        from . import scene_io
        return [o for o in context.selected_objects if scene_io.is_other_layer_wall(o)]

    def invoke(self, context, event):
        if self._other_layer(context):
            return context.window_manager.invoke_props_dialog(self, title="Paredes de outra camada")
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"{len(self._other_layer(context))} parede(s) selecionada(s) foram feitas com o "
                          "construtor antigo.")
        layout.prop(self, "other_walls", expand=True)

    def execute(self, context):
        from . import scene_io
        plan = scene_io.read_plan(context.scene)
        others = self._other_layer(context)
        if others and self.other_walls == 'CONVERT':
            skipped = scene_io.convert_into(plan, others, context.scene)
            if skipped:
                self.report({'WARNING'}, "Sem dados de trechos, ficam como referência: " + ", ".join(skipped))
        session = props.start(plan, context.scene.name)
        from ..measure import scene_cotas
        session.project_height = scene_cotas.ceiling_height(context.scene)
        context.window_manager.btm_wall_editor.new_height = session.project_height   # pé-direito do projeto (D-36)
        try:
            win, area, region = window.open_editor(context)
        except RuntimeError as exc:
            props.end()
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if plan.chains:
            first = plan.chains[0]
            props.session().selected = (0, 0) if first.segment_count() else None
        with context.temp_override(window=win, area=area, region=region):
            bpy.ops.btm.wall_editor_modal('INVOKE_DEFAULT')
        return {'FINISHED'}


class BTM_OT_WallEditorModal(bpy.types.Operator):
    """Interação da planta do Editor de Paredes"""
    bl_idname = "btm.wall_editor_modal"
    bl_label = "Editor de Paredes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _timer = None

    def invoke(self, context, event):
        if props.session() is None:
            return {'CANCELLED'}
        self.dragging = None
        self.panning = None
        self.tab_ready = False
        self._timer = context.window_manager.event_timer_add(TIMER_STEP, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context, apply_changes):
        s = props.session()
        report = None
        if s is not None and apply_changes:
            from . import apply
            report = apply.apply_plan(context, s.plan, remove_modules=s.remove_modules,
                                      project_height=s.project_height if s.equalize_height else None)
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if s is not None:
            # Fecha a janela depois que o modal terminar (não fechar a janela onde o modal está rodando).
            window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)
            props.end()
        return report

    def cancel(self, context):
        self._end(context, False)

    def _local(self, context, event):
        _win, area, region = window.editor_area(context)
        if region is None:
            return None, None
        if self.dragging is None and self.panning is None and window.over_side_panel(area, event.mouse_x,
                                                                                     event.mouse_y):
            return None, None             # painel lateral: os botões e campos recebem o evento
        return region, (event.mouse_x - region.x, event.mouse_y - region.y)

    def modal(self, context, event):
        s = props.session()
        if s is None:
            self._end(context, False)
            return {'CANCELLED'}
        if s.request == 'ok':
            report = self._end(context, True)
            closed = f", {report['closed']} sala(s) fechada(s) no OK" if report.get('closed') else ""
            self.report({'INFO'}, f"Paredes aplicadas: {len(report['created'])} nova(s), {len(report['updated'])} "
                                  f"atualizada(s), {len(report['removed'])} removida(s){closed}.")
            return {'FINISHED'}
        if s.request == 'cancel':
            self._end(context, False)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            if not self.tab_ready:
                _win, area, _region = window.editor_area(context)
                self.tab_ready = window.focus_editor_tab(area)
            return {'PASS_THROUGH'}
        region, pixel = self._local(context, event)
        if region is None:
            return {'PASS_THROUGH'}
        inside = 0 <= pixel[0] <= region.width and 0 <= pixel[1] <= region.height
        if not inside and self.dragging is None and self.panning is None:
            return {'PASS_THROUGH'}       # painéis laterais e cabeçalho
        _win, area, _region = window.editor_area(context)
        view = ensure_view(region, area)
        s.cursor = view.to_world(pixel)
        handled = self._handle(context, event, s, view, pixel)
        s.redraw()
        return {'RUNNING_MODAL'} if handled else {'PASS_THROUGH'}

    # Eventos ------------------------------------------------------------------------------------------------
    def _handle(self, context, event, s, view, pixel):
        state = _state(context)
        if event.type == 'MIDDLEMOUSE':
            self.panning = pixel if event.value == 'PRESS' else None
            return True
        if event.type == 'MOUSEMOVE' and self.panning is not None:
            view.pan(pixel[0] - self.panning[0], pixel[1] - self.panning[1])
            self.panning = pixel
            return True
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            view.zoom(1.15 if event.type == 'WHEELUPMOUSE' else 1 / 1.15, pixel)
            return True
        if event.type == 'HOME' and event.value == 'PRESS':
            view.fit(s.plan.bounds(), margin=0.15)
            return True
        if s.prompt in PROMPTS:
            return self._handle_prompt(context, event, s, pixel)
        if state.tool == 'DRAW':
            return self._handle_draw(context, event, s, view, pixel)
        if event.type == 'ESC' and event.value == 'PRESS':
            if s.typed:
                s.typed = ""                      # Esc primeiro limpa a digitação
            elif s.dirty():
                s.prompt = 'discard'              # pergunta antes de descartar (D-30)
            else:
                s.request = 'cancel'
            return True
        if state.tool == 'SELECT' and self._handle_typing(event, s):
            return True
        if event.type in {'DEL', 'X'} and event.value == 'PRESS' and s.selected is not None:
            remove_segment(s, *s.selected)
            return True
        if event.type == 'LEFTMOUSE':
            return self._handle_click(context, event, s, view, pixel, state.tool)
        if event.type == 'MOUSEMOVE' and self.dragging is not None:
            ci, k = self.dragging
            chain = s.plan.chains[ci]
            prev = k - 1 if k > 0 else (len(chain.nodes) - 1 if chain.closed else None)
            point = s.cursor
            if prev is not None:
                point, _locked = preview_point(context, chain.nodes[prev], point)
            elif state.magnetic:
                point = snap_to_grid(point, state.grid_size)
            if (not chain.closed and k == len(chain.nodes) - 1 and chain.segment_count() >= 3
                    and distance_point_point(pixel, view.to_screen(chain.nodes[0])) <= SNAP_CLOSE_PX):
                point = chain.nodes[0]                       # ímã também no arraste (D-33)
            chain.move_node(k, point)
            return True
        return False

    def _handle_click(self, context, event, s, view, pixel, tool):
        if event.value == 'RELEASE':
            dragged, self.dragging = self.dragging, None
            if dragged is not None:
                ci, k = dragged
                chain = s.plan.chains[ci]
                if (not chain.closed and k == len(chain.nodes) - 1 and chain.segment_count() >= 3
                        and chain.touches_start(chain.nodes[-1], CLOSE_TOLERANCE)):
                    s.prompt, s.prompt_chain = 'close_existing', ci       # arraste até o início (D-34)
            return True
        if event.value != 'PRESS':
            return False
        s.error = ""
        if tool == 'SELECT':
            s.typed = ""
            node = hit_node(s, pixel)
            if node is not None:
                self.dragging = node
                s.selected_node, s.selected = node, None
                return True
            s.selected_node = None
            line = hit_line(s, pixel)
            if line is not None:
                ci, i, which = line
                s.selected, s.line = (ci, i), which
            else:
                s.selected = None
            return True
        if tool == 'REMOVE_NODE':
            node = hit_node(s, pixel)
            if node is not None:
                try:
                    s.plan.chains[node[0]].remove_node(node[1])
                except ValueError as exc:
                    s.error = str(exc)
                s.selected = None
            return True
        line = hit_line(s, pixel)
        if line is None:
            return True
        ci, i, _which = line
        chain = s.plan.chains[ci]
        if tool == 'ADD_NODE':
            chain.split(i, s.cursor)
        elif tool == 'INVERT':
            chain.invert()
        s.selected = None
        return True

    def _handle_typing(self, event, s):
        """Digitação direta da medida na face ou no vértice selecionado (D-27, RF-39)."""
        if event.value != 'PRESS' or (s.selected is None and s.selected_node is None):
            return False
        if event.unicode and event.unicode in "0123456789,.":
            s.typed += event.unicode
            return True
        if event.type == 'BACK_SPACE' and s.typed:
            s.typed = s.typed[:-1]
            return True
        if event.type in {'RET', 'NUMPAD_ENTER'} and s.typed:
            try:
                value = units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
                if s.selected_node is not None:
                    ci, k = s.selected_node
                    chain = s.plan.chains[ci]
                    i = k - 1 if k > 0 else (chain.segment_count() - 1 if chain.closed else None)
                    if i is None:
                        raise ValueError("Valor Inválido: o primeiro vértice de uma parede aberta não tem trecho "
                                         "chegando nele.")
                    chain.set_length(i, value, model.INNER)
                else:
                    chain, i = s.segment()
                    chain.set_length(i, value, s.line)
                s.error = ""
            except ValueError as exc:
                s.error = str(exc)
            s.typed = ""
            return True
        return False

    def _handle_draw(self, context, event, s, view, pixel):
        state = _state(context)
        if event.value != 'PRESS':
            return event.type == 'MOUSEMOVE'
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish_drawing(s)
            return True
        if event.type == 'BACK_SPACE':
            s.typed = s.typed[:-1]
            return True
        if event.unicode and event.unicode in "0123456789,.":
            s.typed += event.unicode
            return True
        if event.type in {'RET', 'NUMPAD_ENTER'} and s.drawing is not None and s.typed:
            try:
                length = units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
            except ValueError as exc:
                s.error = str(exc)
                return True
            start = s.drawing.nodes[-1]
            end, _locked = preview_point(context, start, s.cursor)
            d = math.atan2(end[1] - start[1], end[0] - start[0]) if end != start else 0.0
            target = (start[0] + math.cos(d) * length, start[1] + math.sin(d) * length)
            if s.drawing.segment_count() >= 2 and s.drawing.touches_start(target, CLOSE_TOLERANCE):
                s.typed, s.prompt = "", 'close'           # chegou ao início pelo teclado: pergunta (D-34)
                s.pending_point = target                  # "Não" mantém o trecho digitado
                return True
            self._append(s, state, target)
            return True
        if event.type != 'LEFTMOUSE':
            return False
        point = s.cursor
        node = hit_node(s, pixel)
        if s.drawing is None:
            if node is not None:
                point = s.plan.chains[node[0]].nodes[node[1]]
            elif state.magnetic:
                point = snap_to_grid(point, state.grid_size)
            s.drawing = model.Chain([point], [], False, state.new_direction)
            s.plan.chains.append(s.drawing)
            return True
        if close_snap(s, view, pixel):
            s.prompt = 'close'
            return True
        end, _locked = preview_point(context, s.drawing.nodes[-1], point)
        self._append(s, state, end)
        return True

    def _append(self, s, state, point):
        s.drawing.nodes.append((float(point[0]), float(point[1])))
        s.drawing.segments.append(model.Segment(thickness=state.new_thickness, height=state.new_height))
        s.typed = ""

    def _finish_drawing(self, s):
        if s.drawing is not None and s.drawing.segment_count() == 0:
            s.plan.chains.remove(s.drawing)
        s.drawing, s.typed = None, ""

    def _answer_no(self, context, s):
        if s.prompt == 'close' and getattr(s, 'pending_point', None) is not None and s.drawing is not None:
            self._append(s, _state(context), s.pending_point)
        s.prompt, s.pending_point = None, None

    def _handle_prompt(self, context, event, s, pixel):
        if event.type == 'ESC' and event.value == 'PRESS':
            self._answer_no(context, s)           # Esc fecha a pergunta (= Não)
            return True
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return event.type != 'MOUSEMOVE'
        _win, _area, region = window.editor_area(context)
        _box, yes, no = _prompt_rects(region)
        from ..hb_gpu_draw import point_in_rect
        if point_in_rect(pixel[0], pixel[1], yes):
            if s.prompt == 'discard':
                s.prompt, s.request = None, 'cancel'
                return True
            if s.prompt == 'close_existing':
                chain = s.plan.chains[s.prompt_chain]
                if chain.close_if_touching(CLOSE_TOLERANCE) and not any(sg.source for sg in chain.segments):
                    chain.side = chain.outward_side()
                s.prompt = None
                return True
            s.pending_point = None
            self._append(s, _state(context), s.drawing.nodes[0])
            s.drawing.close()
            s.drawing.side = s.drawing.outward_side()     # sala fechada: espessura para fora (D-25)
            s.drawing, s.prompt = None, None
            _state(context).tool = 'SELECT'
        elif point_in_rect(pixel[0], pixel[1], no):
            self._answer_no(context, s)
        return True


class BTM_OT_WallEditorOk(bpy.types.Operator):
    """Aplica as paredes desenhadas ao ambiente"""
    bl_idname = "btm.wall_editor_ok"
    bl_label = "OK"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        s = props.session()
        if s is None:
            return {'CANCELLED'}
        from . import apply
        missing = apply.items_that_do_not_fit(s.plan)
        modules = apply.modules_of_removed(s.plan)
        mismatched = apply.height_mismatches(s.plan, s.project_height)
        if (missing or modules or mismatched) and not s.confirm_pending:
            s.warnings = [f"{item} não cabe em {wall}" for wall, item in missing]
            s.removed_modules = [f"{item} (em {wall})" for wall, item in modules]
            s.height_mismatches = mismatched
            s.confirm_pending = True
            self.report({'WARNING'}, "Confira os avisos no painel e clique OK de novo para aplicar.")
            return {'CANCELLED'}
        s.request = 'ok'
        return {'FINISHED'}


class BTM_OT_WallEditorCancel(bpy.types.Operator):
    """Fecha o editor sem alterar as paredes"""
    bl_idname = "btm.wall_editor_cancel"
    bl_label = "Cancelar"
    bl_options = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        s = props.session()
        if s is not None and s.dirty():               # D-30: confirmação antes de descartar
            return context.window_manager.invoke_confirm(
                self, event, title="Descartar alterações", message="Descartar as alterações e fechar o editor?",
                confirm_text="Descartar", icon='WARNING')
        return self.execute(context)

    def execute(self, context):
        s = props.session()
        if s is not None:
            s.request = 'cancel'
        return {'FINISHED'}


class BTM_OT_WallEditorFit(bpy.types.Operator):
    """Enquadra todas as paredes na planta"""
    bl_idname = "btm.wall_editor_fit"
    bl_label = "Enquadrar Tudo"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        s = props.session()
        if s is not None and s.view is not None:
            s.view.fit(s.plan.bounds(), margin=0.15)
            s.redraw()
        return {'FINISHED'}


classes = (BTM_OT_WallEditor, BTM_OT_WallEditorModal, BTM_OT_WallEditorOk, BTM_OT_WallEditorCancel,
           BTM_OT_WallEditorFit)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
