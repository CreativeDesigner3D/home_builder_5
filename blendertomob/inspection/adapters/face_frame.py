"""Adaptador face frame (T056; D-20, D-22).

Reaproveita o mecanismo do face frame: cada vão (`IS_FACE_FRAME_OPENING_CAGE`) tem `face_frame_opening.swing_percent`
(0–1) e pivôs `FRONT_PIVOT` posicionados por `solver_face_frame.front_leaves`. A pose é aplicada sem recalcular
(`op_open_mode._apply_swing` com proxy de `swing_percent`) e só o `commit` grava `swing_percent`, que dispara o
recálculo e recria os pivôs. Por isso o contexto da animação é refeito quando um pivô deixa de existir.

Uma `Front` aqui é o vão inteiro (porta dupla abre as duas folhas juntas, como no modo legado).
"""

from mathutils import Euler, Vector  # type: ignore

from .. import fronts, pivot_math

OPENING_TAG = 'IS_FACE_FRAME_OPENING_CAGE'
ROOT_TAG = 'IS_FACE_FRAME_CABINET_CAGE'
PIVOT_ROLE = 'FRONT_PIVOT'
FRONT_ROLES = frozenset({'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT'})


def _modules():
    from ...product_libraries.face_frame import solver_face_frame, types_face_frame
    from ...product_libraries.face_frame.operators import op_open_mode
    return solver_face_frame, types_face_frame, op_open_mode


def _kind(opening):
    props = getattr(opening, 'face_frame_opening', None)
    if props is None:
        return None
    front_type = props.front_type
    if front_type == 'DOOR':
        return {'TOP': fronts.FLIP_UP, 'BOTTOM': fronts.FLIP_DOWN}.get(props.hinge_side, fronts.DOOR)
    if front_type == 'TILT_OUT':
        return fronts.FLIP_DOWN
    if front_type == 'DRAWER_FRONT':
        return fronts.DRAWER
    if front_type == 'PULLOUT':
        return fronts.PULLOUT
    return None   # NONE, FALSE_FRONT, INSET_PANEL, APPLIANCE não abrem


def _openable(opening):
    if not opening.get(OPENING_TAG) or opening.get('IS_MANUAL_FRONT'):
        return False
    if _kind(opening) is None:
        return False
    return any(c.get('hb_part_role') == PIVOT_ROLE for c in opening.children)


class FaceFrameFront(fronts.Front):
    library = 'FACE_FRAME'

    def __init__(self, opening, root):
        pivots = [c for c in opening.children if c.get('hb_part_role') == PIVOT_ROLE]
        representative = next((c for p in pivots for c in p.children_recursive
                               if c.get('hb_part_role') in FRONT_ROLES), opening)
        super().__init__(_kind(opening), root, representative, f"FACE_FRAME:{opening.name}")
        self.opening = opening
        self._ctx = None

    # Conversões --------------------------------------------------------------------------------------------
    def _to_swing(self, value):
        if self.hinged:
            return pivot_math.degrees_to_fraction(value, pivot_math.FACE_FRAME_MAX_ANGLE)
        return pivot_math.clamp_fraction(value)

    def _from_swing(self, swing):
        if self.hinged:
            return pivot_math.fraction_to_degrees(swing, pivot_math.FACE_FRAME_MAX_ANGLE)
        return pivot_math.clamp_fraction(swing)

    def _context(self, rebuild=False):
        if self._ctx is None or rebuild:
            _solver, _types, op_open_mode = _modules()
            self._ctx = op_open_mode._build_tween_context(self.opening)
        return self._ctx

    def _leaves(self, swing):
        solver, _types, op_open_mode = _modules()
        ctx = self._context()
        proxy = op_open_mode._SwingOverrideProxy(ctx['op_props'], swing)
        return solver.front_leaves(ctx['layout'], ctx['rect'], ctx['cab_props'], proxy)

    # Interface ---------------------------------------------------------------------------------------------
    def get(self):
        return self._from_swing(self.opening.face_frame_opening.swing_percent)

    def apply(self, value):
        _solver, _types, op_open_mode = _modules()
        swing = self._to_swing(value)
        for attempt in range(2):
            ctx = self._context(rebuild=attempt > 0)
            if ctx is None:
                return
            try:
                op_open_mode._apply_swing(ctx, swing)
                return
            except ReferenceError:
                continue   # pivôs recriados por um recálculo: refaz o contexto e tenta de novo

    def commit(self, value):
        swing = self._to_swing(value)
        self.apply(value)
        props = self.opening.face_frame_opening
        if abs(props.swing_percent - swing) > 1e-6:
            from ...cutting import stale
            stale.skip_next_update()      # o recálculo abaixo não muda peças: não marcar o plano (D-31)
            props.swing_percent = swing   # dispara o recálculo do gabinete
        self._ctx = None

    def hinge_frame(self):
        ctx = self._context()
        world = self.opening.matrix_world
        rot = world.to_3x3()
        if ctx is None:
            return world.translation.copy(), Vector((0.0, 0.0, 1.0)), Vector((1.0, 0.0, 0.0))
        closed = self._leaves(0.0)
        opened = self._leaves(1.0)
        if not closed:
            return world.translation.copy(), Vector((0.0, 0.0, 1.0)), Vector((1.0, 0.0, 0.0))
        pivot = Vector(closed[0]['pivot_position'])
        if self.hinged:
            # Eixo pela diferença de rotação do pivô entre fechado e aberto.
            r0 = Euler(closed[0]['pivot_rotation']).to_matrix()
            r1 = Euler(opened[0]['pivot_rotation']).to_matrix()
            axis, _angle = (r1 @ r0.inverted()).to_quaternion().to_axis_angle()
            offset = Vector(closed[0].get('part_position', (1.0, 0.0, 0.0)))
            ref = r0 @ (offset if offset.length > 1e-9 else Vector((1.0, 0.0, 0.0)))
            return world @ pivot, (rot @ axis).normalized(), (rot @ ref).normalized()
        direction = Vector(opened[0]['pivot_position']) - pivot
        if direction.length < 1e-9:
            direction = Vector((0.0, -1.0, 0.0))
        return world @ pivot, (rot @ direction).normalized(), Vector((0.0, 0.0, 1.0))

    def travel(self):
        closed, opened = self._leaves(0.0), self._leaves(1.0)
        if not closed or not opened:
            return 0.0
        world = self.opening.matrix_world.to_3x3()
        return (world @ (Vector(opened[0]['pivot_position']) - Vector(closed[0]['pivot_position']))).length

    def objects(self):
        objs = []
        for pivot in (c for c in self.opening.children if c.get('hb_part_role') == PIVOT_ROLE):
            objs.extend(c for c in pivot.children_recursive if c.type in {'MESH', 'CURVE'})
        return objs or [self.obj]

    def is_valid(self):
        try:
            return self.opening.name is not None
        except ReferenceError:
            return False


def find_fronts(scene):
    _solver, types_face_frame, _op = _modules()
    found = []
    for obj in scene.objects:
        if obj.get(OPENING_TAG) and _openable(obj):
            root = types_face_frame.find_cabinet_root(obj)
            if root is not None:
                found.append(FaceFrameFront(obj, root))
    return found


def front_for_object(obj, scene):
    _solver, types_face_frame, _op = _modules()
    current = obj
    via_front = False   # só vale se o clique veio de uma frente ou do pivô dela (não de uma prateleira do vão)
    while current is not None:
        if current.get('hb_part_role') in FRONT_ROLES or current.get('hb_part_role') == PIVOT_ROLE:
            via_front = True
        if current.get(OPENING_TAG):
            if not via_front or not _openable(current):
                return None
            root = types_face_frame.find_cabinet_root(current)
            return FaceFrameFront(current, root) if root is not None else None
        if current.get(ROOT_TAG):
            return None
        current = current.parent
    return None
