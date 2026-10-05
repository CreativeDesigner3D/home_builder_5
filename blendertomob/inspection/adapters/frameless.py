"""Adaptador frameless (T054, T055; D-21).

As frentes do frameless não tinham conceito de abertura. Aqui elas abrem sem objetos novos e sem tocar nos drivers
de medida: a pose vai para `delta_rotation_euler` / `delta_location` da própria peça, e o valor fica na idprop
`btm_open` (ausente = fechada).

A dobradiça é deduzida da geometria avaliada da peça (caixa local): a origem da peça fica numa quina; o comprimento
(X local) é a altura da frente, a largura (Y local) vai até a borda livre e a espessura (Z local) aponta para a face
frontal. Isso cobre porta esquerda, direita, dupla e as portas de canto (rotações diferentes) com a mesma regra.
"""

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ... import compat
from .. import fronts, pivot_math

ROOT_TAG = 'IS_FRAMELESS_CABINET_CAGE'
VALUE_PROP = 'btm_open'
CUTPART_GROUP = 'GeoNodeCutpart'
DRAWER_BOX_TAG = 'IS_DRAWER_BOX'
FALLBACK_TRAVEL = 0.4  # m, sem caixa de gaveta nem profundidade conhecida


def _kind(obj):
    if obj.get('IS_FLIP_UP_DOOR'):
        return fronts.FLIP_UP
    if obj.get('IS_DOOR_FRONT'):
        return fronts.DOOR
    if obj.get('IS_PULLOUT_FRONT'):
        return fronts.PULLOUT
    if obj.get('IS_DRAWER_FRONT'):
        return fronts.DRAWER
    return None


def _root(obj):
    current = obj.parent
    while current is not None:
        if current.get(ROOT_TAG):
            return current
        current = current.parent
    return None


def _has_cutpart(obj):
    return any(m.type == 'NODES' and m.node_group and m.node_group.name.split('.')[0] == CUTPART_GROUP
               for m in obj.modifiers)


def _openable(obj):
    if _kind(obj) is None or not _has_cutpart(obj):
        return False
    if obj.hide_viewport:          # folha oculta por `driver_hide` (ex.: porta direita com "Door Swing" esquerda)
        return False
    if obj.get('False Front'):     # frente falsa não abre
        return False
    return _root(obj) is not None


def _extent(min_value, max_value):
    """Lado da caixa local que se afasta da origem (com sinal)."""
    return max_value if abs(max_value) >= abs(min_value) else min_value


def _local_frame(obj):
    """(comprimento, largura, espessura) no espaço do pai, com a rotação fechada (sem os deltas)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = [Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
    ext = [_extent(min(c[i] for c in corners), max(c[i] for c in corners)) for i in range(3)]
    sx, sy, sz = obj.scale
    rotation = tuple(tuple(row) for row in obj.rotation_euler.to_matrix())
    return pivot_math.frame_from_extents(rotation, (ext[0] * sx, 0.0, 0.0), (0.0, ext[1] * sy, 0.0),
                                         (0.0, 0.0, ext[2] * sz))


def _travel(obj):
    """Curso da gaveta: profundidade da caixa (filha da frente) ou do vão."""
    for child in obj.children:
        if child.get(DRAWER_BOX_TAG):
            for mod in child.modifiers:
                if mod.type == 'NODES':
                    depth = compat.try_get_gn_input(mod, 'Dim Y', None)
                    if depth:
                        return abs(float(depth))
    parent = obj.parent
    if parent is not None:
        for mod in parent.modifiers:
            if mod.type == 'NODES':
                depth = compat.try_get_gn_input(mod, 'Dim Y', None)
                if depth:
                    return max(abs(float(depth)) - 0.0254, 0.05)
    return FALLBACK_TRAVEL


class FramelessFront(fronts.Front):
    library = 'FRAMELESS'

    def __init__(self, obj, root):
        super().__init__(_kind(obj), root, obj, f"FRAMELESS:{obj.name}")
        self._hinge = None
        self._slide_dir = None
        self._travel = None

    def _prepare(self):
        if self._hinge is not None or self._slide_dir is not None:
            return
        length_dir, width_dir, thickness_dir = _local_frame(self.obj)
        if self.kind == fronts.DOOR:
            self._hinge = pivot_math.side_hinge(length_dir, width_dir, thickness_dir)
        elif self.kind == fronts.FLIP_UP:
            self._hinge = pivot_math.top_hinge(length_dir, width_dir, thickness_dir)
        else:
            self._slide_dir = pivot_math.normalize(thickness_dir)
            self._travel = _travel(self.obj)

    def get(self):
        return self.clamp(self.obj.get(VALUE_PROP, 0.0))

    def apply(self, value):
        value = self.clamp(value)
        if value <= 0.0:
            self.obj.delta_rotation_euler = (0.0, 0.0, 0.0)
            self.obj.delta_location = (0.0, 0.0, 0.0)
            return
        self._prepare()
        if self.hinged:
            euler, offset = pivot_math.pose_for(self._hinge, value)
            self.obj.delta_rotation_euler = euler
            self.obj.delta_location = offset
        else:
            self.obj.delta_rotation_euler = (0.0, 0.0, 0.0)
            self.obj.delta_location = pivot_math.slide(self._slide_dir, self._travel, value)

    def commit(self, value):
        value = self.clamp(value)
        self.apply(value)
        if value <= 0.0:
            if VALUE_PROP in self.obj:
                del self.obj[VALUE_PROP]
        else:
            self.obj[VALUE_PROP] = float(value)

    def _parent_matrix(self):
        parent = self.obj.parent
        base = parent.matrix_world if parent is not None else Matrix.Identity(4)
        return base @ self.obj.matrix_parent_inverse

    def hinge_frame(self):
        self._prepare()
        matrix = self._parent_matrix()
        rot = matrix.to_3x3()
        origin = Vector(self.obj.location)
        if self.hinged:
            point = matrix @ (origin + Vector(self._hinge['hinge_offset']))
            axis = (rot @ Vector(self._hinge['axis'])).normalized()
            ref = (rot @ Vector(self._hinge['free'])).normalized()
            # Sentido positivo do controle = sentido de abrir.
            sign = pivot_math.swing_sign(self._hinge['axis'], self._hinge['free'], self._hinge['outward'])
            return point, axis * sign, ref
        point = matrix @ origin
        direction = (rot @ Vector(self._slide_dir)).normalized()
        return point, direction, Vector((0.0, 0.0, 1.0))

    def travel(self):
        self._prepare()
        return self._travel or 0.0

    def objects(self):
        return [self.obj] + [c for c in self.obj.children_recursive if c.type in {'MESH', 'CURVE'}]


def find_fronts(scene):
    found = []
    for obj in scene.objects:
        if obj.type == 'MESH' and _openable(obj):
            found.append(FramelessFront(obj, _root(obj)))
    return found


def front_for_object(obj, scene):
    current = obj
    while current is not None:
        if current.type == 'MESH' and _openable(current):
            return FramelessFront(current, _root(current))
        if current.get(ROOT_TAG):
            return None
        current = current.parent
    return None

