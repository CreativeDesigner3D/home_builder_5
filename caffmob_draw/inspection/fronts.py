"""Frentes inspecionáveis de todas as linhas de produto (T048; D-19).

Uma `Front` é uma porta, basculante, gaveta ou pullout que pode abrir. Cada linha de produto (frameless, face frame,
closets, o módulo rápido `btm` e as portas de ambiente) tem um adaptador em `inspection/adapters/` que encontra as frentes e sabe aplicar
o valor de abertura sem recalcular o módulo:

- `get()`: valor atual (graus para articuladas, fração do curso para gavetas);
- `apply(valor)`: só a pose (usada na animação e no arraste do controle);
- `commit(valor)`: pose e estado persistente da linha;
- `hinge_frame()`: (origem, eixo, direção de referência) em coordenadas do mundo, para o controle no 3D.
"""

from . import pivot_math

DOOR = 'DOOR'
FLIP_UP = 'FLIP_UP'
FLIP_DOWN = 'FLIP_DOWN'
DRAWER = 'DRAWER'
PULLOUT = 'PULLOUT'

HINGED = frozenset({DOOR, FLIP_UP, FLIP_DOWN})
KIND_LABELS = {DOOR: "Porta", FLIP_UP: "Basculante", FLIP_DOWN: "Basculante p/ baixo", DRAWER: "Gaveta",
               PULLOUT: "Pullout"}


class Front:
    """Base dos adaptadores. Subclasses implementam `get`, `apply`, `commit`, `hinge_frame` e `objects`."""

    library = ""

    def __init__(self, kind, module_root, obj, key):
        self.kind = kind
        self.module_root = module_root
        self.obj = obj          # objeto representativo (clique, seleção e rótulo)
        self.key = key          # identificador estável na sessão (para animações e a proteção ao salvar)

    @property
    def hinged(self):
        return self.kind in HINGED

    @property
    def max_value(self):
        return pivot_math.MAX_ANGLE if self.hinged else 1.0

    @property
    def label(self):
        return f"{KIND_LABELS.get(self.kind, self.kind)} — {self.obj.name}"

    def clamp(self, value):
        return pivot_math.clamp_angle(value) if self.hinged else pivot_math.clamp_fraction(value)

    def is_open(self):
        return self.get() > (0.5 if self.hinged else 0.005)

    def open_value(self, degrees=pivot_math.MAX_ANGLE):
        """Valor de "aberta": o ângulo pedido para articuladas, curso total para gavetas."""
        return self.clamp(degrees) if self.hinged else 1.0

    # Interface dos adaptadores -------------------------------------------------------------------------------
    def get(self):
        raise NotImplementedError

    def apply(self, value):
        raise NotImplementedError

    def commit(self, value):
        raise NotImplementedError

    def hinge_frame(self):
        raise NotImplementedError

    def objects(self):
        """Objetos que se movem com a frente (para clique e para o envelope de interferência)."""
        return [self.obj]

    def can_sweep(self):
        """Pode ser girada na verificação de interferência sem criar objetos (porta de ambiente sem folha: não)."""
        return True

    def is_valid(self):
        try:
            return self.obj.name is not None and self.module_root.name is not None
        except ReferenceError:
            return False


def _adapters():
    from .adapters import aggregate_leaf, btm, closets, face_frame, frameless, room_doors
    return (frameless, face_frame, closets, btm, room_doors, aggregate_leaf)


def iter_fronts(scene):
    """Todas as frentes inspecionáveis da cena, de todas as linhas."""
    fronts = []
    for adapter in _adapters():
        fronts.extend(adapter.find_fronts(scene))
    return fronts


def fronts_of(module_root, scene):
    return [f for f in iter_fronts(scene) if f.module_root == module_root]


def front_for_object(obj, scene):
    """Frente dona de `obj` (o próprio objeto ou um filho dela, como o puxador); None se não houver."""
    if obj is None:
        return None
    for adapter in _adapters():
        front = adapter.front_for_object(obj, scene)
        if front is not None:
            return front
    return None


def module_root_of(obj):
    """Raiz do módulo que contém `obj`, em qualquer linha."""
    tags = ('IS_FRAMELESS_CABINET_CAGE', 'IS_FACE_FRAME_CABINET_CAGE', 'IS_CLOSET_STARTER_CAGE',
            'IS_ENTRY_DOOR_BP')        # porta de ambiente: a própria porta faz o papel do módulo (D-20)
    current = obj
    while current is not None:
        if any(current.get(tag) for tag in tags):
            return current
        plane = getattr(current, 'btm_plane', None)
        if plane is not None and getattr(plane, 'object_kind', '') == 'MODULE':
            return current
        current = current.parent
    return None
