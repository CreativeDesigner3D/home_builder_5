"""Adaptador das portas de ambiente do Home Builder 5 (T016; D-20, RF-20).

Uma `Front` é a porta inteira (as duas folhas da porta dupla abrem juntas). A folha 3D só é criada quando a porta é
aberta pela primeira vez (`room_door_leaf.ensure_leaves`); enquanto ela não existe, a porta conta como fechada e
salvar/abrir tudo não cria nada. O estado gravado é `btm_open` (graus) na porta, como nas outras linhas.
"""

import math

from mathutils import Vector  # type: ignore

from .. import fronts, room_door_leaf


class RoomDoorFront(fronts.Front):
    library = 'ROOM'

    def __init__(self, door):
        super().__init__(fronts.DOOR, door, door, f"ROOM:{door.name}")

    @property
    def label(self):
        return f"Porta de ambiente — {self.obj.name}"

    def get(self):
        pivots = room_door_leaf.pivots_of(self.module_root)
        if not pivots:
            return 0.0
        return abs(math.degrees(pivots[0].rotation_euler.z))

    def apply(self, value):
        value = self.clamp(value)
        if value <= 0.0 and not room_door_leaf.pivots_of(self.module_root):
            return                                  # fechada e sem folha: nada a criar
        for spec, pivot in room_door_leaf.ensure_leaves(self.module_root):
            pivot.rotation_euler.z = math.radians(spec.rot_sign * value)

    def commit(self, value):
        self.apply(value)
        self.module_root['btm_open'] = float(self.clamp(value))

    def can_sweep(self):
        return bool(room_door_leaf.pivots_of(self.module_root))   # sem folha ainda: não cria só para verificar

    def hinge_frame(self):
        spec = room_door_leaf.leaf_specs(self.module_root)[0]
        world = self.module_root.matrix_world
        rot = world.to_3x3()
        origin = world @ Vector((spec.hinge_x, spec.hinge_y, 0.0))
        axis = (rot @ Vector((0.0, 0.0, spec.rot_sign))).normalized()
        return origin, axis, (rot @ Vector((spec.dx, 0.0, 0.0))).normalized()

    def objects(self):
        pivots = room_door_leaf.pivots_of(self.module_root)
        return [leaf for p in pivots for leaf in p.children] or [self.module_root]


def find_fronts(scene):
    return [RoomDoorFront(obj) for obj in scene.objects if room_door_leaf.is_room_door(obj)]


def front_for_object(obj, scene):
    current = obj
    while current is not None:
        if room_door_leaf.is_room_door(current):
            return RoomDoorFront(current)
        current = current.parent
    return None
