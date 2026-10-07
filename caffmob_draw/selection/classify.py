"""Tipo do objeto selecionado, para todas as bibliotecas (T001; D-09, RN-01).

Dado um objeto, `classify(obj)` devolve `Classified(kind, obj, root, library)`:
- `kind`: o que o usuário selecionou (ver KINDS);
- `obj`: o objeto que representa o tipo (a frente, a porta de ambiente, a parede…);
- `root`: o módulo dono (para frente e peça interna) ou o próprio objeto;
- `library`: FRAMELESS, FACE_FRAME, CLOSETS, BTM (módulo rápido/camada nova) ou HB (estrutura do ambiente).

A precedência segue RN-01: frente e peça antes do módulo, módulo antes da parede. Isso importa porque gabinetes são
filhos da parede e subir pela hierarquia passa por ela (mesma razão da exclusão em `operators/ops_general.py`).
Só usa `.get()`, `.parent` e atributos simples, então funciona com objetos simulados nos testes.
"""

from collections import namedtuple

Classified = namedtuple('Classified', 'kind obj root library')

ANNOTATION, FRONT, PART, MODULE = 'ANNOTATION', 'FRONT', 'PART', 'MODULE'
ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE = 'ROOM_DOOR', 'WINDOW', 'GEOMETRY', 'OBSTACLE'
WALL, FLOOR, CEILING, OTHER = 'WALL', 'FLOOR', 'CEILING', 'OTHER'
KINDS = (ANNOTATION, FRONT, PART, MODULE, ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE, WALL, FLOOR, CEILING, OTHER)

KIND_LABELS = {
    ANNOTATION: "Cota / anotação", FRONT: "Frente", PART: "Peça", MODULE: "Módulo", ROOM_DOOR: "Porta",
    WINDOW: "Janela", GEOMETRY: "Geometria", OBSTACLE: "Obstáculo", WALL: "Parede", FLOOR: "Piso",
    CEILING: "Teto", OTHER: "Objeto",
}
LIBRARY_LABELS = {'FRAMELESS': "Frameless", 'FACE_FRAME': "Face frame", 'CLOSETS': "Closets",
                  'BTM': "Módulo rápido", 'HB': "Ambiente"}

MODULE_TAGS = (
    ('IS_FRAMELESS_CABINET_CAGE', 'FRAMELESS'),
    ('IS_FACE_FRAME_CABINET_CAGE', 'FACE_FRAME'),
    ('IS_FACE_FRAME_PRODUCT_CAGE', 'FACE_FRAME'),
    ('IS_CLOSET_STARTER_CAGE', 'CLOSETS'),
)
FRONT_TAGS = ('IS_DOOR_FRONT', 'IS_DRAWER_FRONT', 'IS_PULLOUT_FRONT', 'IS_FLIP_UP_DOOR', 'IS_CABINET_FRONT')
FRONT_ROLES = frozenset({'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT', 'FRONT_PIVOT',
                         'CLOSET_DOOR_FRONT', 'CLOSET_DRAWER_FRONT'})
BTM_FRONT_SUFFIXES = ('_Door_L', '_Door_R', '_Door_Flip')


def _btm_kind(obj):
    plane = getattr(obj, 'btm_plane', None)
    return getattr(plane, 'object_kind', '') if plane is not None else ''


def module_library(obj):
    """Biblioteca se `obj` é a raiz de um módulo; senão None."""
    for tag, library in MODULE_TAGS:
        if obj.get(tag):
            return library
    if _btm_kind(obj) == 'MODULE':
        return 'BTM'
    return None


def _is_front(obj):
    if any(obj.get(tag) for tag in FRONT_TAGS) or obj.get('hb_part_role') in FRONT_ROLES:
        return True
    return obj.name.endswith(BTM_FRONT_SUFFIXES)


def _ancestors(obj):
    current = obj
    while current is not None:
        yield current
        current = current.parent


def module_root(obj):
    """Raiz do módulo que contém `obj` (ou o próprio), com a biblioteca; (None, None) se não houver."""
    for node in _ancestors(obj):
        library = module_library(node)
        if library:
            return node, library
    return None, None


def classify(obj):
    if obj is None:
        return None
    if obj.get('IS_2D_ANNOTATION'):
        return Classified(ANNOTATION, obj, obj, 'HB')

    root, library = module_root(obj)
    if root is not None:
        # Frente: o primeiro ancestral (até o módulo) que é frente.
        for node in _ancestors(obj):
            if node is root:
                break
            if _is_front(node):
                return Classified(FRONT, node, root, library)
        if obj is root:
            return Classified(MODULE, root, root, library)
        return Classified(PART, obj, root, library)

    for node in _ancestors(obj):
        if node.get('IS_ENTRY_DOOR_BP'):
            return Classified(ROOM_DOOR, node, node, 'HB')
        if node.get('IS_WINDOW_BP'):
            return Classified(WINDOW, node, node, 'HB')
        kind = _btm_kind(node)
        if kind == 'OPENING':
            return Classified(WINDOW, node, node, 'BTM')
        if kind == 'GEOMETRY':
            return Classified(GEOMETRY, node, node, 'BTM')
        if node.get('IS_OBSTACLE') or node.get('IS_SOFFIT_BP'):
            return Classified(OBSTACLE, node, node, 'HB')
        if node.get('IS_WALL_BP'):
            return Classified(WALL, node, node, 'HB')
        if kind == 'WALL':
            return Classified(WALL, node, node, 'BTM')
        if node.get('IS_FLOOR_BP') or kind == 'FLOOR':
            return Classified(FLOOR, node, node, 'HB' if node.get('IS_FLOOR_BP') else 'BTM')
        if node.get('IS_CEILING_BP'):
            return Classified(CEILING, node, node, 'HB')
    return Classified(OTHER, obj, obj, '')


def movable_root(obj):
    """Objeto que se move no "Mover Sobre" (RN-05): o módulo para frentes e peças; geometria e obstáculo; None
    para parede, piso, teto, cota e objetos não reconhecidos."""
    info = classify(obj)
    if info is None:
        return None
    if info.kind in (FRONT, PART, MODULE, GEOMETRY, OBSTACLE):
        return info.root
    return None


def reference_root(obj):
    """Objeto que pode ser referência (B) no "Mover Sobre": tudo que é movível e também paredes."""
    info = classify(obj)
    if info is None:
        return None
    if info.kind == WALL:
        return info.obj
    return movable_root(obj)
