"""Adaptador do módulo rápido `btm_cabinet` (T060; D-32).

As portas do módulo rápido (`<módulo>_Door_L`, `_Door_R`, `_Door_Flip`) giram por drivers que leem o Y local do
Empty `<módulo>_Controller` (0 a 0,2 m → 0° a 90°; `geometry/door_controller.py`). O adaptador escreve nesse Empty;
`btm_cabinet.door_open` acompanha pelo driver de sincronização. Uma `Front` é o módulo inteiro (todas as folhas
abrem juntas).
"""

from mathutils import Vector  # type: ignore

from .. import fronts, pivot_math

CONTROLLER_SUFFIX = '_Controller'
DOOR_SUFFIXES = ('_Door_L', '_Door_R', '_Door_Flip')
TRAVEL = 0.2  # m de curso do controlador para 90°


def _controller(module):
    return next((c for c in module.children if c.name.endswith(CONTROLLER_SUFFIX)), None)


def _doors(module):
    return [c for c in module.children if c.name.endswith(DOOR_SUFFIXES)]


def _is_module(obj):
    plane = getattr(obj, 'btm_plane', None)
    cabinet = getattr(obj, 'btm_cabinet', None)
    return (plane is not None and plane.object_kind == 'MODULE' and cabinet is not None
            and cabinet.door_swing != 'NONE' and _controller(obj) is not None and bool(_doors(obj)))


class BtmFront(fronts.Front):
    library = 'BTM'

    def __init__(self, module):
        kind = fronts.FLIP_UP if module.btm_cabinet.door_swing == 'FLIP' else fronts.DOOR
        doors = _doors(module)
        super().__init__(kind, module, doors[0], f"BTM:{module.name}")

    def get(self):
        controller = _controller(self.module_root)
        if controller is None:
            return 0.0
        return pivot_math.fraction_to_degrees(controller.location.y / TRAVEL, pivot_math.BTM_MAX_ANGLE)

    def apply(self, value):
        controller = _controller(self.module_root)
        if controller is not None:
            controller.location.y = pivot_math.degrees_to_fraction(value, pivot_math.BTM_MAX_ANGLE) * TRAVEL

    def commit(self, value):
        self.apply(value)
        self.module_root['btm_open'] = float(self.clamp(value))

    def hinge_frame(self):
        world = self.module_root.matrix_world
        rot = world.to_3x3()
        door = self.obj
        point = world @ Vector(door.location)
        if self.kind == fronts.FLIP_UP:
            return point, (rot @ Vector((-1.0, 0.0, 0.0))).normalized(), (rot @ Vector((0.0, 0.0, -1.0))).normalized()
        if door.name.endswith('_Door_R'):
            return point, (rot @ Vector((0.0, 0.0, -1.0))).normalized(), (rot @ Vector((-1.0, 0.0, 0.0))).normalized()
        return point, (rot @ Vector((0.0, 0.0, 1.0))).normalized(), (rot @ Vector((1.0, 0.0, 0.0))).normalized()

    def objects(self):
        return _doors(self.module_root)


def find_fronts(scene):
    return [BtmFront(obj) for obj in scene.objects if obj.type == 'MESH' and _is_module(obj)]


def front_for_object(obj, scene):
    current = obj
    while current is not None:
        if current.type == 'MESH' and _is_module(current):
            return BtmFront(current)
        current = current.parent
    return None
