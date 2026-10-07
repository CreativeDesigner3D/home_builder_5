"""Adaptador closets (T058; D-22, D-23).

Usa as funções do próprio closets: `apply_door_open(porta, fração)` (gira em torno da dobradiça com os parâmetros
guardados no layout, `hb_door_cx/cy/cz/leaf/side` + `hb_hinge`) e `apply_drawer_open(frente, fração)` (desliza a
frente e a caixa). O estado fica em `hb_door_open` / `hb_drawer_open`, agora fracionário (0–1, M-05).
"""

from mathutils import Matrix, Vector  # type: ignore

from .. import fronts, pivot_math

ROOT_TAG = 'IS_CLOSET_STARTER_CAGE'


def _types():
    from ...product_libraries.closets import types_closets
    return types_closets


def _kind(obj):
    types_closets = _types()
    role = obj.get('hb_part_role')
    if role == types_closets.PART_ROLE_DOOR and obj.get('hb_door_cx') is not None:
        return fronts.DOOR
    if role == types_closets.PART_ROLE_DRAWER_FRONT and obj.get('hb_slide_dist') is not None:
        return fronts.DRAWER
    return None


class ClosetFront(fronts.Front):
    library = 'CLOSETS'

    def __init__(self, obj, root):
        super().__init__(_kind(obj), root, obj, f"CLOSETS:{obj.name}")

    @property
    def _key(self):
        return 'hb_door_open' if self.kind == fronts.DOOR else 'hb_drawer_open'

    def _to_fraction(self, value):
        if self.hinged:
            return pivot_math.degrees_to_fraction(value, pivot_math.CLOSETS_MAX_ANGLE)
        return pivot_math.clamp_fraction(value)

    def get(self):
        fraction = _types().open_fraction(self.obj, self._key)
        if self.hinged:
            return pivot_math.fraction_to_degrees(fraction, pivot_math.CLOSETS_MAX_ANGLE)
        return fraction

    def apply(self, value):
        types_closets = _types()
        fraction = self._to_fraction(value)
        if self.hinged:
            types_closets.apply_door_open(self.obj, fraction)
        else:
            types_closets.apply_drawer_open(self.obj, fraction)

    def commit(self, value):
        self.apply(value)
        self.obj[self._key] = float(self._to_fraction(value))

    def _parent_matrix(self):
        parent = self.obj.parent
        base = parent.matrix_world if parent is not None else Matrix.Identity(4)
        return base @ self.obj.matrix_parent_inverse

    def hinge_frame(self):
        matrix = self._parent_matrix()
        rot = matrix.to_3x3()
        obj = self.obj
        if self.hinged:
            cx, cy, cz = obj.get('hb_door_cx', 0.0), obj.get('hb_door_cy', 0.0), obj.get('hb_door_cz', 0.0)
            leaf = obj.get('hb_door_leaf', 0.0)
            back = obj.get('hb_door_side', 'FRONT') == 'BACK'
            if obj.get('hb_hinge', 'LEFT') == 'LEFT':
                point, ref, sign = Vector((cx, cy, cz)), Vector((1.0, 0.0, 0.0)), -1.0
            else:
                point, ref, sign = Vector((cx + leaf, cy, cz)), Vector((-1.0, 0.0, 0.0)), 1.0
            if back:
                sign = -sign
            return matrix @ point, (rot @ Vector((0.0, 0.0, sign))).normalized(), (rot @ ref).normalized()
        y0 = obj.get('hb_slide_y0', obj.location.y)
        side = -1.0 if obj.get('hb_door_side', 'FRONT') != 'BACK' else 1.0
        point = matrix @ Vector((obj.location.x, y0, obj.location.z))
        return point, (rot @ Vector((0.0, side, 0.0))).normalized(), Vector((0.0, 0.0, 1.0))

    def travel(self):
        return float(self.obj.get('hb_slide_dist', 0.0)) if not self.hinged else 0.0

    def objects(self):
        objs = [self.obj] + [c for c in self.obj.children_recursive if c.type in {'MESH', 'CURVE'}]
        if self.kind == fronts.DRAWER and self.obj.parent is not None:
            types_closets = _types()
            index = self.obj.get('hb_drawer_index', 0)
            objs.extend(c for c in self.obj.parent.children
                        if c.get('hb_part_role') == types_closets.PART_ROLE_DRAWER_BOX
                        and c.get('hb_drawer_index', 0) == index)
        return objs


def find_fronts(scene):
    types_closets = _types()
    found = []
    for obj in scene.objects:
        if _kind(obj) is not None:
            root = types_closets.find_starter_root(obj)
            if root is not None:
                found.append(ClosetFront(obj, root))
    return found


def front_for_object(obj, scene):
    types_closets = _types()
    current = obj
    while current is not None:
        if _kind(current) is not None:
            root = types_closets.find_starter_root(current)
            return ClosetFront(current, root) if root is not None else None
        if current.get('hb_part_role') == types_closets.PART_ROLE_DRAWER_BOX and current.parent is not None:
            index = current.get('hb_drawer_index', 0)
            for sibling in current.parent.children:
                if (sibling.get('hb_part_role') == types_closets.PART_ROLE_DRAWER_FRONT
                        and sibling.get('hb_drawer_index', 0) == index and _kind(sibling) is not None):
                    root = types_closets.find_starter_root(sibling)
                    return ClosetFront(sibling, root) if root is not None else None
        if current.get(ROOT_TAG):
            return None
        current = current.parent
    return None

