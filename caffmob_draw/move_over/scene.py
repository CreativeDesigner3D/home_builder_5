"""Camada de cena do "Mover Sobre" (T017; D-16, RN-05, RN-08, RN-09, RN-11).

- A (arrastado) e B (referência) são as raízes devolvidas pelo classificador (frente e peça contam como o módulo).
- As caixas são calculadas no referencial de B (posição e rotação de B, sem escala); A assume a rotação de B antes do
  alinhamento (RN-08). Todas as bibliotecas e o módulo rápido têm a frente em −Y e o fundo em Y ≈ 0; uma parede como B
  tem a face da frente em Y = 0 (os módulos ficam do lado −Y).
- Se B está numa parede, A passa a ser filho dessa parede (mantendo a posição no mundo), para as cotas continuarem
  valendo. `restore()` devolve pai e posição originais.
"""

import math

from mathutils import Matrix, Vector  # type: ignore

from ..selection import classify
from . import align, reposition


def _frame(obj):
    loc, rot, _scale = obj.matrix_world.decompose()
    return Matrix.LocRotScale(loc, rot, None)


def _local_box(obj, depsgraph):
    """Caixa do objeto no seu espaço local, já com a escala do objeto."""
    evaluated = obj.evaluated_get(depsgraph)
    _loc, _rot, scale = obj.matrix_world.decompose()
    corners = [Vector((c[0] * scale.x, c[1] * scale.y, c[2] * scale.z)) for c in evaluated.bound_box]
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def _wall_of(obj):
    parent = obj.parent
    return parent if parent is not None and parent.get('IS_WALL_BP') else None


class MoveOver:
    def __init__(self, context, obj_a, obj_b):
        self.context = context
        self.a = classify.movable_root(obj_a)
        self.b = classify.reference_root(obj_b)
        if self.a is None or self.b is None or self.a == self.b:
            raise ValueError("Esses objetos não podem ser usados no Mover Sobre.")
        info_b = classify.classify(self.b)
        self.b_is_wall = info_b.kind == classify.WALL
        self.original_parent = self.a.parent
        self.original_matrix = self.a.matrix_world.copy()
        self.original_parent_inverse = self.a.matrix_parent_inverse.copy()
        depsgraph = context.evaluated_depsgraph_get()
        self.b_frame = _frame(self.b)
        self.b_frame_inv = self.b_frame.inverted()
        self.box_b = _local_box(self.b, depsgraph)
        self.a_local_box = _local_box(self.a, depsgraph)
        _loc, _rot, self.a_scale = self.a.matrix_world.decompose()
        self.origin_in_b = self.b_frame_inv @ self.original_matrix.translation
        self.delta = Vector((0.0, 0.0, 0.0))
        self.rotation = 0.0       # graus em torno do eixo vertical, pelo centro da base de A (feature 003, D-21)

    # Caixas ---------------------------------------------------------------------------------------------
    def _unrotated_box(self, delta=None):
        d = self.delta if delta is None else Vector(delta)
        offset = self.origin_in_b + d
        lo, hi = self.a_local_box
        return (tuple(lo[i] + offset[i] for i in range(3)), tuple(hi[i] + offset[i] for i in range(3)))

    def box_a(self, delta=None):
        """Caixa de A no referencial de B, com a rotação de B, a rotação pedida e o deslocamento atual."""
        box = self._unrotated_box(delta)
        return reposition.rotated_box(box, self.rotation) if self.rotation else box

    def original_box_a(self):
        """Caixa de A como está antes de mexer (rotação original), no referencial de B — para a tela inicial."""
        depsgraph = self.context.evaluated_depsgraph_get()
        evaluated = self.a.evaluated_get(depsgraph)
        corners = [self.b_frame_inv @ (self.original_matrix @ Vector(c)) for c in evaluated.bound_box]
        return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))

    # Alinhar --------------------------------------------------------------------------------------------
    def align_to(self, targets):
        """Aplica os alvos (lista de `align.Target`) sobre a posição atual; devolve o novo deslocamento."""
        step = align.combine(targets, self.box_a(), self.box_b, self.b_is_wall)
        for i in range(3):
            if step[i]:
                self.delta[i] += step[i]
        self.preview()
        return tuple(self.delta)

    def set_gap(self, axis, value):
        """Define a distância de A a B num eixo (0 = X, 1 = profundidade, 2 = altura), como nos campos da janela."""
        box_a, box_b = self.box_a(), self.box_b
        if axis == 0:
            # Mantém o lado em que A está: à direita de B se o centro de A estiver à direita.
            if (box_a[0][0] + box_a[1][0]) >= (box_b[0][0] + box_b[1][0]):
                self.delta[0] += (box_b[1][0] + value) - box_a[0][0]
            else:
                self.delta[0] += (box_b[0][0] - value) - box_a[1][0]
        elif axis == 1:
            self.delta[1] += (box_b[0][1] + value) - box_a[0][1]
        else:
            self.delta[2] += (box_b[0][2] + value) - box_a[0][2]
        self.preview()

    def gaps(self):
        return align.gaps(self.box_a(), self.box_b)

    # Cena -----------------------------------------------------------------------------------------------
    def _target_matrix(self):
        local = self.origin_in_b + self.delta
        if self.rotation:
            local = Vector(reposition.origin_after_rotation(tuple(local), self._unrotated_box(), self.rotation))
        loc = self.b_frame @ local
        _l, rot, _s = self.b_frame.decompose()
        if self.rotation:
            rot = rot @ Matrix.Rotation(math.radians(self.rotation), 3, 'Z').to_quaternion()
        return Matrix.LocRotScale(loc, rot, self.a_scale)

    # Reposicionar (feature 003, RF-22 a RF-26) --------------------------------------------------------------
    def set_rotation(self, degrees):
        self.rotation = float(degrees) % 360.0
        self.preview()

    def nudge(self, delta):
        for i in range(3):
            self.delta[i] += delta[i]
        self.preview()

    def world_min(self):
        """Canto mínimo de A no projeto (valores absolutos, só exibição)."""
        return tuple(self.b_frame @ Vector(self.box_a()[0]))

    def set_world(self, axis, value):
        """Move A para o canto mínimo dele ficar em `value` no eixo `axis` do projeto (modo absoluto)."""
        current = Vector(self.world_min())
        target = current.copy()
        target[axis] = value
        self.delta += self.b_frame_inv.to_3x3() @ (target - current)
        self.preview()

    def saved(self):
        return reposition.save_position(self.box_a(), self.box_b, self.rotation)

    def apply_saved(self, saved):
        self.rotation = float(saved['rotation']) % 360.0
        step = reposition.apply_position(saved, self.box_a(), self.box_b)
        for i in range(3):
            self.delta[i] += step[i]
        self.preview()

    def preview(self):
        wall = _wall_of(self.b) if not self.b_is_wall else self.b
        if wall is not None and self.a.parent != wall:
            self.a.parent = wall
            self.a.matrix_parent_inverse = Matrix.Identity(4)
        self.a.matrix_world = self._target_matrix()

    def restore(self):
        self.a.parent = self.original_parent
        self.a.matrix_parent_inverse = self.original_parent_inverse
        self.a.matrix_world = self.original_matrix

    def overlapping(self):
        """Módulos (fora A) cuja caixa no mundo cruza a de A na posição atual (RN-11)."""
        depsgraph = self.context.evaluated_depsgraph_get()
        corners = [self._target_matrix() @ Vector(c) for c in self.a.evaluated_get(depsgraph).bound_box]
        box = (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))
        found = []
        for obj in self.context.scene.objects:
            if obj == self.a or not classify.module_library(obj):
                continue
            ev = obj.evaluated_get(depsgraph)
            oc = [obj.matrix_world @ Vector(c) for c in ev.bound_box]
            other = (tuple(min(c[i] for c in oc) for i in range(3)), tuple(max(c[i] for c in oc) for i in range(3)))
            if align.overlaps(box, other, tolerance=1e-3):
                found.append(obj)
        return found
