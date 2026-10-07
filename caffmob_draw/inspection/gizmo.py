"""Controle de abertura no 3D (T068; D-25).

Com uma frente (ou peça dela) ativa e selecionada, aparece um controle giratório (`GIZMO_GT_dial_3d`) no eixo da
dobradiça das portas e basculantes, ou uma seta (`GIZMO_GT_arrow_3d`) no sentido do curso das gavetas.

- Arrastar aplica só a pose (`Front.apply`), sem recalcular o módulo.
- Perto de 0°, 45° e 90° o valor encaixa (opção `btm_inspection.snap_stops`).
- Ao soltar, o valor é gravado (`Front.commit`) num timer. Fazer isso dentro do desenho do gizmo seria arriscado:
  no face frame, gravar recalcula o gabinete e recria objetos.
"""

import math

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from . import fronts, pivot_math

_state = {'front': None, 'pending': None, 'pointer': 0}


def _active_front(context):
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    cached = _state['front']
    if cached is not None and _state['pointer'] == obj.as_pointer() and cached.is_valid():
        return cached
    front = fronts.front_for_object(obj, context.scene)
    _state['front'] = front
    _state['pointer'] = obj.as_pointer() if front is not None else 0
    return front


def _frame_matrix(point, axis, ref):
    z = Vector(axis).normalized()
    x = Vector(ref) - z * Vector(ref).dot(z)
    x = x.normalized() if x.length > 1e-9 else z.orthogonal().normalized()
    y = z.cross(x)
    return Matrix(((x.x, y.x, z.x, point.x), (x.y, y.y, z.y, point.y), (x.z, y.z, z.z, point.z), (0, 0, 0, 1)))


def _snap(context, degrees):
    state = getattr(context.window_manager, 'btm_inspection', None)
    if state is not None and state.snap_stops:
        return pivot_math.snap_angle(degrees)
    return pivot_math.clamp_angle(degrees)


def _commit_pending():
    front, value = _state['front'], _state['pending']
    _state['pending'] = None
    if front is not None and value is not None:
        try:
            front.commit(value)
        except ReferenceError:
            pass
    return None


class BTM_GGT_front_open(bpy.types.GizmoGroup):
    bl_idname = "BTM_GGT_front_open"
    bl_label = "Abertura de portas e gavetas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        return _active_front(context) is not None

    # Valores ligados ao gizmo -------------------------------------------------------------------------------
    def _dial_get(self):
        front = _state['front']
        if front is None:
            return 0.0
        value = _state['pending'] if _state['pending'] is not None else front.get()
        return math.radians(value)

    def _dial_set(self, value):
        front = _state['front']
        if front is None:
            return
        degrees = _snap(bpy.context, math.degrees(value))
        front.apply(degrees)
        _state['pending'] = degrees

    def _arrow_get(self):
        front = _state['front']
        if front is None or front.hinged:      # a seta é só das gavetas; portas não têm curso (D-31)
            return 0.0
        value = _state['pending'] if _state['pending'] is not None else front.get()
        return value * max(front.travel(), 1e-6)

    def _arrow_set(self, value):
        front = _state['front']
        if front is None or front.hinged:
            return
        fraction = pivot_math.clamp_fraction(value / max(front.travel(), 1e-6))
        front.apply(fraction)
        _state['pending'] = fraction

    # Ciclo do grupo ----------------------------------------------------------------------------------------
    def setup(self, context):
        dial = self.gizmos.new("GIZMO_GT_dial_3d")
        dial.target_set_handler("offset", get=self._dial_get, set=self._dial_set)
        try:
            dial.draw_options = {'ANGLE_VALUE'}
        except (AttributeError, TypeError):
            pass
        dial.use_draw_value = True
        dial.line_width = 3.0
        dial.scale_basis = 0.6
        dial.color = (0.95, 0.55, 0.1)
        dial.alpha = 0.6
        dial.color_highlight = (1.0, 0.75, 0.2)
        dial.alpha_highlight = 1.0

        arrow = self.gizmos.new("GIZMO_GT_arrow_3d")
        arrow.target_set_handler("offset", get=self._arrow_get, set=self._arrow_set)
        arrow.use_draw_value = True
        arrow.scale_basis = 1.0
        arrow.color = (0.95, 0.55, 0.1)
        arrow.alpha = 0.6
        arrow.color_highlight = (1.0, 0.75, 0.2)
        arrow.alpha_highlight = 1.0
        self.dial, self.arrow = dial, arrow

    def refresh(self, context):
        self._place(context)

    def draw_prepare(self, context):
        self._place(context)
        # Soltou o controle: grava o valor fora do desenho.
        if (_state['pending'] is not None and not self.dial.is_modal and not self.arrow.is_modal
                and not bpy.app.timers.is_registered(_commit_pending)):
            bpy.app.timers.register(_commit_pending, first_interval=0.0)

    def _place(self, context):
        front = _active_front(context)
        if front is None:
            self.dial.hide = self.arrow.hide = True
            return
        try:
            point, axis, ref = front.hinge_frame()
        except (ReferenceError, AttributeError, ValueError):
            self.dial.hide = self.arrow.hide = True
            return
        matrix = _frame_matrix(Vector(point), axis, ref)
        self.dial.hide = not front.hinged
        self.arrow.hide = front.hinged
        if front.hinged:
            self.dial.matrix_basis = matrix
        else:
            self.arrow.matrix_basis = matrix


def register():
    bpy.utils.register_class(BTM_GGT_front_open)


def unregister():
    if bpy.app.timers.is_registered(_commit_pending):
        bpy.app.timers.unregister(_commit_pending)
    _state.update(front=None, pending=None, pointer=0)
    bpy.utils.unregister_class(BTM_GGT_front_open)
