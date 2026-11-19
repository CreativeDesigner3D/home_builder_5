"""Islands on the drawings.

An island has no wall, but the Elevation View's printing only needs
what a wall gives it: a frame to look along, a length and a height, the
products that stand in front of it, and somewhere to keep the drafter's
edits. A Side stands in for the wall on each of the island's four
sides, so an island side is dimensioned, labelled and noted by the very
rules a wall elevation is.
"""

import math

import bpy
from mathutils import Matrix, Vector

from ..operators import elevation_mode as em

SIDES = ('FRONT', 'BACK', 'LEFT', 'RIGHT')
SIDE_NAMES = {'FRONT': "Front", 'BACK': "Back", 'LEFT': "Left End",
              'RIGHT': "Right End"}


class Side:
    """One side of an island, in the place of a wall. Its frame runs
    left to right as the viewer standing at that side sees the island,
    y = 0 on the island's far face, -y towards the viewer; what is kept
    on a wall (its notes, moved dimensions) is kept on the island's
    group under the side's name."""

    is_stand_in = True
    type = 'EMPTY'
    parent = None

    def __init__(self, group, side, frame, length, height, roots):
        self.group = group
        self.side = side
        self.name = f"{group.name}: {SIDE_NAMES[side]}"
        self.matrix_world = frame
        self.stand_in_frame = frame
        self.stand_in_dims = (length, height, 0.0)
        self.children = list(roots)
        self.bound_box = [(x, 0.0, z) for x in (0.0, length)
                          for z in (0.0, height) for _ in (0, 1)]
        # The products whose fronts face this side. A side none face
        # (an end, the back of a one-sided island) is drawn plain: its
        # outline, not the insides of cabinets seen from behind.
        toward = frame.to_3x3() @ Vector((0.0, -1.0, 0.0))
        self.facing = {p.name for p in _products(group)
                       if (p.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0)))
                       .normalized().dot(toward) > 0.7}
        self.plain = not self.facing

    def filter_items(self, items):
        """What the elevation shows from this side: the products facing
        it, and whatever else is not hidden behind them."""
        if self.plain:
            return items
        front = [it for it in items if it.obj.name in self.facing]

        def hidden(it):
            return any(min(it.x1, f.x1) - max(it.x0, f.x0) > 0.0254
                       for f in front)
        return [it for it in items
                if it.obj.name in self.facing
                or (em._is_product(it.obj) and not hidden(it))
                or not em._is_product(it.obj)]

    @property
    def children_recursive(self):
        out = []
        for root in self.children:
            out.append(root)
            out.extend(root.children_recursive)
        return out

    def _key(self, key):
        return f"{key}@{self.side}"

    def get(self, key, default=None):
        return self.group.get(self._key(key), default)

    def __getitem__(self, key):
        return self.group[self._key(key)]

    def __setitem__(self, key, value):
        self.group[self._key(key)] = value

    def __delitem__(self, key):
        del self.group[self._key(key)]

    def __contains__(self, key):
        return self._key(key) in self.group

    def keys(self):
        tail = '@' + self.side
        return [k[:-len(tail)] for k in self.group.keys() if k.endswith(tail)]

    def __eq__(self, other):
        return isinstance(other, Side) and other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def visible_get(self, *_a, **_k):
        return True

    def hide_get(self, *_a, **_k):
        return False


def _products(group):
    return [c for c in group.children if em._is_product(c)]


def islands(scene):
    """The room's islands: groups of products standing free of the
    walls, biggest first."""
    out = []
    for obj in scene.objects:
        # Cages never render: a group is an island by what it holds.
        if obj.parent is not None or not obj.get('IS_CAGE_GROUP') \
                or obj.get('IS_WALL_BP'):
            continue
        if _products(obj):
            out.append(obj)
    return sorted(out, key=lambda g: g.name)


def _width(obj):
    xs = [c[0] for c in obj.bound_box]
    return max(xs) - min(xs)


def _box(group):
    """(G, x0, x1, y0, y1, z1): the group's level frame and its products'
    extent in it."""
    # Square to the island's widest product, its front the way that
    # product's front faces (a cabinet's front is its -y).
    mw = group.matrix_world
    products = _products(group)
    if not products:
        return None
    lead = max(products, key=_width)
    yaw = lead.matrix_world.to_euler().z
    G = Matrix.Translation(Vector((mw.translation.x, mw.translation.y,
                                   0.0))) @ Matrix.Rotation(yaw, 4, 'Z')
    Gi = G.inverted_safe()
    pts = []
    for p in products:
        pts += [Gi @ (p.matrix_world @ Vector(c)) for c in p.bound_box]
    if not pts:
        return None
    return (G, min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts),
            max(p.z for p in pts))


def _tops(scene, group, G, box):
    """Countertops standing loose over the island: shown with it."""
    x0, x1, y0, y1 = box
    Gi = G.inverted_safe()
    out = []
    for obj in scene.objects:
        if obj.parent is not None or not obj.get('IS_COUNTERTOP'):
            continue
        c = Gi @ obj.matrix_world.translation
        if x0 - 0.3 <= c.x <= x1 + 0.3 and y0 - 0.3 <= c.y <= y1 + 0.3:
            out.append(obj)
    return out


def sides(scene, group):
    """{side: Side} of an island group, each registered so a view can
    find it by name."""
    found = _box(group)
    if found is None:
        return {}
    G, x0, x1, y0, y1, z1 = found
    if min(x1 - x0, y1 - y0, z1) < 0.0254:
        return {}               # nothing there to draw
    roots = [group] + _tops(scene, group, G, (x0, x1, y0, y1))
    # Each side: where its frame starts, which way it faces, how long.
    spec = {'FRONT': ((x0, y1), 0.0, x1 - x0),
            'BACK': ((x1, y0), math.pi, x1 - x0),
            'LEFT': ((x1, y1), -math.pi / 2.0, y1 - y0),
            'RIGHT': ((x0, y0), math.pi / 2.0, y1 - y0)}
    out = {}
    for side in SIDES:
        (sx, sy), turn, length = spec[side]
        # The viewer of the FRONT stands at -y looking +y: the frame's
        # x is the group's x and the far face (y1) is y = 0.
        frame = (G @ Matrix.Translation(Vector((sx, sy, 0.0)))
                 @ Matrix.Rotation(turn, 4, 'Z'))
        out[side] = em.register_stand_in(
            Side(group, side, frame, length, z1, roots))
    return out
