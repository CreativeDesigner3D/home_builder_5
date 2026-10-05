"""Abrir/fechar frentes e o modo de inspeção (T063, T064; D-24, D-26, D-27).

Abrir portas é inspeção (RN-14): os operadores usam `{'REGISTER'}` sem `UNDO` para não encher o histórico de desfazer,
como o modo legado do face frame.
"""

import time

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore

from . import fronts

ANIM_DURATION = 0.35
TIMER_HZ = 60

# Operador de inspeção em execução (lido pelo HUD, pelo gizmo e pelo handler de plano desatualizado).
_active = None


def inspection_running():
    return _active is not None


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def default_angle(context):
    state = getattr(context.window_manager, 'btm_inspection', None)
    return float(state.default_angle) if state is not None else 90.0


def scope_fronts(context, scope):
    """Frentes do escopo: 'ALL' (projeto), 'SELECTED' (seleção) ou 'ACTIVE_MODULE' (módulo do objeto ativo)."""
    scene = context.scene
    if scope == 'ALL':
        return fronts.iter_fronts(scene)
    if scope == 'ACTIVE_MODULE':
        root = fronts.module_root_of(context.active_object) if context.active_object else None
        return fronts.fronts_of(root, scene) if root is not None else []
    selected = list(context.selected_objects)
    found, keys = [], set()
    roots = {fronts.module_root_of(o) for o in selected} - {None}
    candidates = [f for f in fronts.iter_fronts(scene) if f.module_root in roots] if roots else []
    for obj in selected:
        front = fronts.front_for_object(obj, scene)
        if front is not None:
            candidates.append(front)
    for front in candidates:
        if front.key not in keys:
            keys.add(front.key)
            found.append(front)
    return found


class BTM_OT_FrontsSetOpen(bpy.types.Operator):
    """Abre ou fecha portas, basculantes e gavetas para inspeção (o arquivo é salvo fechado)"""
    bl_idname = "btm.fronts_set_open"
    bl_label = "Abrir/Fechar Frentes"
    bl_options = {'REGISTER'}

    scope: bpy.props.EnumProperty(
        name="Escopo",
        items=[('ALL', "Projeto", "Todas as frentes do projeto"),
               ('SELECTED', "Selecionados", "Frentes dos módulos e peças selecionados"),
               ('ACTIVE_MODULE', "Módulo ativo", "Frentes do módulo do objeto ativo")],
        default='ALL')  # type: ignore
    mode: bpy.props.EnumProperty(
        name="Ação",
        items=[('CLOSE', "Fechar", "Fecha tudo"), ('OPEN_45', "Abrir 45°", "Portas a 45°, gavetas pela metade"),
               ('OPEN_90', "Abrir 90°", "Portas a 90°, gavetas no curso total")],
        default='OPEN_90')  # type: ignore

    def execute(self, context):
        targets = scope_fronts(context, self.scope)
        if not targets:
            self.report({'WARNING'}, "Nenhuma porta, basculante ou gaveta encontrada.")
            return {'CANCELLED'}
        degrees = {'CLOSE': 0.0, 'OPEN_45': 45.0, 'OPEN_90': 90.0}[self.mode]
        for front in targets:
            value = front.open_value(degrees) if front.hinged else degrees / 90.0
            try:
                front.commit(value)
            except ReferenceError:
                continue
        verb = "fechadas" if self.mode == 'CLOSE' else "abertas"
        self.report({'INFO'}, f"{len(targets)} frente(s) {verb}.")
        return {'FINISHED'}


def _raycast(context, event):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None
    coord = (event.mouse_region_x, event.mouse_region_y)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    hit, _loc, _normal, _index, obj, _matrix = context.scene.ray_cast(
        context.evaluated_depsgraph_get(), origin, direction)
    return obj if hit else None


def _click_on_widget(context, event):
    """Cliques no HUD e nas pílulas do overlay do closets passam adiante (ex.: a pílula "Open Door" desliga o modo)."""
    mx, my = event.mouse_region_x, event.mouse_region_y
    try:
        from ..operators.viewport_hud import click_hits_widget
        if click_hits_widget(context, context.area, mx, my):
            return True
    except (ImportError, AttributeError):
        pass
    try:
        from ..product_libraries.closets import gpu_overlay_closets as overlay
        mode = overlay._active_mode(context)
        for _label, _key, (x, y, w, h) in overlay._filter_pill_rects(context, context.area, mode):
            if x <= mx <= x + w and y <= my <= y + h:
                return True
    except (ImportError, AttributeError, TypeError, ValueError):
        pass
    return False


class BTM_OT_InspectFronts(bpy.types.Operator):
    """Modo de inspeção: clique em portas, basculantes e gavetas para abrir ou fechar. Esc ou botão direito sai"""
    bl_idname = "btm.inspect_fronts"
    bl_label = "Abrir Portas e Gavetas"
    bl_options = {'REGISTER'}

    _timer = None
    _tweens = None
    _exit_requested = False
    _exit_timer = None

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        global _active
        if _active is not None:
            # Segundo clique no botão: pede para o modo em execução sair.
            _active._exit_requested = True
            if _active._exit_timer is None:
                _active._exit_timer = context.window_manager.event_timer_add(0.001, window=context.window)
            return {'CANCELLED'}
        self._tweens = {}
        self._exit_requested = False
        self._exit_timer = None
        self._timer = context.window_manager.event_timer_add(1.0 / TIMER_HZ, window=context.window)
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            "Abrir portas e gavetas  |  Clique: abrir/fechar  |  Esc / botão direito: sair")
        from ..operators.viewport_hud import register_active_modal
        register_active_modal(self)
        _active = self
        state = getattr(context.window_manager, 'btm_inspection', None)
        if state is not None:
            state.active = True
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    # Animação ----------------------------------------------------------------------------------------------
    def _current(self, tween, now):
        t = min(1.0, (now - tween['t0']) / ANIM_DURATION)
        return tween['start'] + (tween['target'] - tween['start']) * _smoothstep(t)

    def _toggle(self, context, front):
        now = time.perf_counter()
        tween = self._tweens.get(front.key)
        if tween is not None:
            # Clique durante a animação inverte a partir da posição atual.
            current = self._current(tween, now)
            target = 0.0 if tween['target'] > 0.0 else tween['open']
            tween.update(start=current, target=target, t0=now)
            return
        current = front.get()
        opened = front.open_value(default_angle(context))
        self._tweens[front.key] = {'front': front, 'start': current, 'target': 0.0 if front.is_open() else opened,
                                   'open': opened, 't0': now}

    def _step(self, context):
        if not self._tweens:
            return
        now = time.perf_counter()
        for key in list(self._tweens):
            tween = self._tweens[key]
            front = tween['front']
            try:
                if now - tween['t0'] >= ANIM_DURATION:
                    front.commit(tween['target'])
                    del self._tweens[key]
                else:
                    front.apply(self._current(tween, now))
            except (ReferenceError, AttributeError):
                del self._tweens[key]   # objetos apagados durante a animação
        if context.area:
            context.area.tag_redraw()

    # Saída -------------------------------------------------------------------------------------------------
    def _finish(self, context):
        global _active
        for tween in (self._tweens or {}).values():
            try:
                tween['front'].commit(tween['target'])
            except (ReferenceError, AttributeError):
                pass
        self._tweens = {}
        wm = context.window_manager
        for timer in (self._timer, self._exit_timer):
            if timer is not None:
                try:
                    wm.event_timer_remove(timer)
                except (ValueError, RuntimeError):
                    pass
        self._timer = self._exit_timer = None
        from ..operators.viewport_hud import unregister_active_modal
        unregister_active_modal(self)
        if _active is self:
            _active = None
        state = getattr(wm, 'btm_inspection', None)
        if state is not None:
            state.active = False
        try:
            context.workspace.status_text_set(None)
        except (AttributeError, RuntimeError):
            pass
        if context.area:
            context.area.tag_redraw()

    def cancel(self, context):
        self._finish(context)

    def modal(self, context, event):
        if self._exit_requested:
            self._finish(context)
            return {'FINISHED'}
        if event.type == 'TIMER':
            self._step(context)
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if _click_on_widget(context, event):
                return {'PASS_THROUGH'}
            front = fronts.front_for_object(_raycast(context, event), context.scene)
            if front is not None:
                self._toggle(context, front)
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._finish(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


classes = (BTM_OT_FrontsSetOpen, BTM_OT_InspectFronts)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _active
    _active = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
