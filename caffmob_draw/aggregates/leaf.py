"""Folha de porta convertida de uma malha (feature 003, T049, T052; RN-11, RN-11a, D-17 a D-19).

Mesmo padrão das portas de ambiente (`inspection/room_door_leaf.py`): um Empty de pivô ("<folha> - Eixo"), filho do
pai, com a malha como filha dele. Giro: eixo na aresta esquerda/direita (vertical) ou de cima/de baixo (horizontal) da
caixa da folha, na face da frente (−Y do pai, a frente dos módulos); correr: o pivô desliza em ±X do pai.
A pose fechada fica guardada (`btm_leaf_rest`, espaço do pai) e abrir nunca altera a malha.
`open_value` é a fração da abertura (0 a 1): graus = fração × ângulo máximo; metros = fração × curso.
"""

import math

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from . import apply, sweep

PIVOT_SUFFIX = " - Eixo"
REST_KEY = 'btm_leaf_rest'
OPEN_KEY = 'btm_open_fraction'
# Sinal do ângulo para abrir "para fora" (para −Y do pai); "para dentro" inverte.
OUT_SIGN = {'LEFT': -1.0, 'RIGHT': 1.0, 'TOP': -1.0, 'BOTTOM': 1.0}


def _matrix(values):
    return Matrix([list(values[i * 4:(i + 1) * 4]) for i in range(4)])


def rest_matrix(obj):
    return _matrix(obj[REST_KEY]) if REST_KEY in obj else None


def leaf_box(obj):
    """Caixa da folha fechada no espaço do pai."""
    rest = rest_matrix(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = [rest @ Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
    return Vector([min(c[i] for c in corners) for i in range(3)]), Vector([max(c[i] for c in corners) for i in range(3)])


def base_point(box, motion, hinge):
    lo, hi = box
    if motion == 'SLIDE':
        return Vector(lo)
    if hinge == 'LEFT':
        return Vector((lo.x, lo.y, lo.z))
    if hinge == 'RIGHT':
        return Vector((hi.x, lo.y, lo.z))
    if hinge == 'TOP':
        return Vector((lo.x, lo.y, hi.z))
    return Vector((lo.x, lo.y, lo.z))         # BOTTOM


def swing_angle(agg, fraction):
    sign = OUT_SIGN[agg.hinge] * (1.0 if agg.swing_sign == 'OUT' else -1.0)
    return sign * math.radians(max(0.0, min(1.0, fraction)) * agg.max_angle)


def pose_matrix(agg, base, fraction):
    """Matriz do pivô no espaço do pai para a abertura `fraction`."""
    if agg.motion == 'SLIDE':
        direction = Vector((1.0 if agg.slide_dir == 'POS_X' else -1.0, 0.0, 0.0))
        return Matrix.Translation(base + direction * agg.travel * max(0.0, min(1.0, fraction)))
    axis = 'Z' if agg.hinge in ('LEFT', 'RIGHT') else 'X'
    return Matrix.Translation(base) @ Matrix.Rotation(swing_angle(agg, fraction), 4, axis)


def pivot_of(obj):
    pivot = obj.btm_aggregate.pivot
    try:
        return pivot if pivot is not None and pivot.name in bpy.data.objects else None
    except ReferenceError:
        return None


def _base(obj):
    pivot = pivot_of(obj)
    return Vector(pivot['btm_leaf_base']) if pivot is not None and 'btm_leaf_base' in pivot else None


def apply_fraction(obj, fraction):
    """Só a pose (sem testar contato): usada na verificação de interferência e no salvar fechado."""
    pivot = pivot_of(obj)
    if pivot is None:
        return
    pivot.matrix_basis = pose_matrix(obj.btm_aggregate, _base(obj), fraction)
    pivot[OPEN_KEY] = float(fraction)


def current_fraction(obj):
    pivot = pivot_of(obj)
    return float(pivot.get(OPEN_KEY, 0.0)) if pivot is not None else 0.0


def rebuild_pivot(obj):
    """Cria ou refaz o pivô a partir da pose fechada e das opções de giro/correr."""
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    if agg.kind != 'LEAF' or parent is None or REST_KEY not in obj:
        return None
    base = base_point(leaf_box(obj), agg.motion, agg.hinge)
    pivot = pivot_of(obj)
    if pivot is None:
        pivot = bpy.data.objects.new(obj.name + PIVOT_SUFFIX, None)
        pivot.empty_display_type = 'SINGLE_ARROW' if agg.motion == 'SWING' else 'PLAIN_AXES'
        pivot.empty_display_size = 0.1
        for collection in obj.users_collection or parent.users_collection:
            collection.objects.link(pivot)
        agg.pivot = pivot
    pivot['btm_leaf'] = obj.name
    pivot['btm_leaf_base'] = list(base)
    pivot.parent = parent
    pivot.matrix_parent_inverse = Matrix.Identity(4)
    obj.parent = pivot
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Translation(-base) @ rest_matrix(obj)
    apply_fraction(obj, 0.0)
    update_open(obj, bpy.context)
    return pivot


def make_leaf(obj, parent, motion='SWING', hinge='LEFT', swing_sign='OUT', max_angle=90.0, slide_dir='POS_X',
              travel=0.5):
    """Converte `obj` em folha de porta de `parent` (sem mexer na malha)."""
    agg = obj.btm_aggregate
    if not agg.is_aggregate:
        agg.orig_parent = obj.parent
        agg.orig_matrix = [v for row in obj.matrix_world for v in row]
    obj[REST_KEY] = [v for row in (parent.matrix_world.inverted() @ obj.matrix_world) for v in row]
    for name, value in (('kind', 'LEAF'), ('motion', motion), ('hinge', hinge), ('swing_sign', swing_sign),
                        ('max_angle', max_angle), ('slide_dir', slide_dir), ('travel', travel), ('open_value', 0.0)):
        apply._write(obj, name, value)
    agg.parent_ref = parent
    agg.is_aggregate = True
    agg.contact_name = ""
    return rebuild_pivot(obj)


def remove_pivot(obj):
    """Volta a folha à pose fechada, filha direta do pai, e apaga o pivô."""
    pivot = pivot_of(obj)
    parent = obj.btm_aggregate.parent_ref
    rest = rest_matrix(obj)
    if parent is not None and rest is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = rest
    if pivot is not None:
        bpy.data.objects.remove(pivot, do_unlink=True)
    obj.btm_aggregate.pivot = None
    if REST_KEY in obj:
        del obj[REST_KEY]


def update_open(obj, context):
    """Leva a folha até `open_value`, parando no primeiro contato ao abrir (RN-11a)."""
    agg = obj.btm_aggregate
    if agg.kind != 'LEAF' or pivot_of(obj) is None:
        return
    from . import collision
    target = max(0.0, min(1.0, agg.open_value))
    current = current_fraction(obj)
    if agg.motion == 'SLIDE':
        scale, step, tolerance = agg.travel, sweep.SLIDE_STEP, sweep.SLIDE_TOLERANCE
    else:
        scale, step, tolerance = agg.max_angle, sweep.SWING_STEP, sweep.SWING_TOLERANCE
    if scale <= 0.0:
        return
    tester = collision.Tester(obj)
    reached, contact = sweep.sweep(current * scale, target * scale, lambda v: tester.hit(v / scale), step,
                                   tolerance)
    fraction = reached / scale
    apply_fraction(obj, fraction)
    agg.contact_name = contact.name if contact is not None and hasattr(contact, 'name') else ""
    if abs(fraction - agg.open_value) > 1e-6:
        apply._write(obj, 'open_value', fraction)
    if context is not None and context.screen is not None:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
