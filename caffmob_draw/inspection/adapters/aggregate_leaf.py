"""Adaptador das folhas de porta convertidas de malhas (feature 003, T050; D-17, D-18).

Com ele, "Abrir/Fechar Frentes", o controle giratório, a verificação de interferência e o salvar fechado da 001
valem também para as folhas convertidas. Valores como nas outras linhas: graus no giro (até o máximo da folha) e
fração do curso no correr. `apply` só posiciona (sem testar contato); `commit` grava `open_value`, que passa pela
parada na batida (`aggregates/leaf.update_open`).
"""

import math

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ...aggregates import leaf
from .. import fronts, pivot_math


def is_leaf(obj):
    agg = getattr(obj, 'btm_aggregate', None)
    return agg is not None and agg.is_aggregate and agg.kind == 'LEAF' and leaf.pivot_of(obj) is not None


class AggregateLeafFront(fronts.Front):
    library = 'AGGREGATE'

    def __init__(self, obj):
        agg = obj.btm_aggregate
        kind = fronts.DOOR if agg.motion == 'SWING' else fronts.DRAWER
        root = fronts.module_root_of(agg.parent_ref) or agg.parent_ref
        super().__init__(kind, root, obj, f"LEAF:{obj.name}")

    @property
    def label(self):
        return f"Folha — {self.obj.name}"

    @property
    def max_value(self):
        return self.obj.btm_aggregate.max_angle if self.hinged else 1.0

    def clamp(self, value):
        if self.hinged:
            return pivot_math.clamp_angle(value, self.obj.btm_aggregate.max_angle)
        return pivot_math.clamp_fraction(value)

    def open_value(self, degrees=pivot_math.MAX_ANGLE):
        return self.clamp(degrees) if self.hinged else 1.0

    def _to_fraction(self, value):
        agg = self.obj.btm_aggregate
        return self.clamp(value) / agg.max_angle if self.hinged else self.clamp(value)

    def get(self):
        fraction = leaf.current_fraction(self.obj)
        return fraction * self.obj.btm_aggregate.max_angle if self.hinged else fraction

    def apply(self, value):
        leaf.apply_fraction(self.obj, self._to_fraction(value))

    def commit(self, value):
        self.obj.btm_aggregate.open_value = self._to_fraction(value)

    def hinge_frame(self):
        agg = self.obj.btm_aggregate
        world = agg.parent_ref.matrix_world
        base = Vector(leaf.pivot_of(self.obj)['btm_leaf_base'])
        rot = world.to_3x3()
        if agg.motion == 'SLIDE':
            axis = Vector((0.0, 0.0, 1.0))
            reference = Vector((1.0 if agg.slide_dir == 'POS_X' else -1.0, 0.0, 0.0))
        else:
            axis = Vector((0.0, 0.0, 1.0)) if agg.hinge in ('LEFT', 'RIGHT') else Vector((1.0, 0.0, 0.0))
            axis *= math.copysign(1.0, leaf.swing_angle(agg, 1.0) or 1.0)
            reference = Vector((1.0, 0.0, 0.0)) if agg.hinge == 'LEFT' else Vector((-1.0, 0.0, 0.0))
            if agg.hinge in ('TOP', 'BOTTOM'):
                reference = Vector((0.0, 0.0, -1.0 if agg.hinge == 'TOP' else 1.0))
        return world @ base, (rot @ axis).normalized(), (rot @ reference).normalized()

    def objects(self):
        return [self.obj] + list(self.obj.children_recursive)

    def is_valid(self):
        try:
            return self.obj.name in bpy.data.objects and is_leaf(self.obj)
        except ReferenceError:
            return False


def find_fronts(scene):
    return [AggregateLeafFront(obj) for obj in scene.objects if is_leaf(obj)]


def front_for_object(obj, scene):
    current = obj
    while current is not None:
        if is_leaf(current):
            return AggregateLeafFront(current)
        pivot_leaf = current.get('btm_leaf') if hasattr(current, 'get') else None
        if pivot_leaf and bpy.data.objects.get(pivot_leaf) is not None and is_leaf(bpy.data.objects[pivot_leaf]):
            return AggregateLeafFront(bpy.data.objects[pivot_leaf])
        current = current.parent
    return None
