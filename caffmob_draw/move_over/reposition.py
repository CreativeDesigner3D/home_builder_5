"""Reposicionar no "Mover Sobre" ampliado (feature 003, T005; RF-22 a RF-26, D-21, D-22). Python puro.

Tudo no referencial de B (a referência), como em `align.py`: caixas `(lo, hi)`, X = largura, Y = profundidade
(frente em −Y), Z = altura. A rotação é em graus em torno do eixo vertical que passa pelo centro da base de A.
"""

import math


def box_center_base(box):
    lo, hi = box
    return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2])


def rotate_point_z(point, center, degrees):
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    x, y = point[0] - center[0], point[1] - center[1]
    return (center[0] + c * x - s * y, center[1] + s * x + c * y, point[2])


def origin_after_rotation(origin, box, degrees):
    """Nova origem de A ao girá-lo `degrees` em torno do centro da base da sua caixa (o centro não se move)."""
    return rotate_point_z(origin, box_center_base(box), degrees)


def rotated_box(box, degrees):
    """Caixa alinhada que envolve `box` girada em torno do centro da base (para as vistas e as distâncias)."""
    lo, hi = box
    center = box_center_base(box)
    corners = [rotate_point_z((x, y, lo[2]), center, degrees) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])]
    xs, ys = [c[0] for c in corners], [c[1] for c in corners]
    return (min(xs), min(ys), lo[2]), (max(xs), max(ys), hi[2])


def step_delta(key, step):
    """Deslocamento de uma tecla do passo: setas em X/profundidade, Page Up/Down em altura."""
    moves = {'RIGHT_ARROW': (step, 0.0, 0.0), 'LEFT_ARROW': (-step, 0.0, 0.0),
             'UP_ARROW': (0.0, step, 0.0), 'DOWN_ARROW': (0.0, -step, 0.0),
             'PAGE_UP': (0.0, 0.0, step), 'PAGE_DOWN': (0.0, 0.0, -step)}
    return moves.get(key)


def absolute_values(b_matrix_apply, box_a):
    """Posição absoluta para exibir: canto mínimo de A levado ao mundo por `b_matrix_apply(ponto)`."""
    return tuple(b_matrix_apply(box_a[0]))


def side_of(box_a, box_b):
    """'LEFT' ou 'RIGHT': lado de B em que está o centro de A."""
    return 'RIGHT' if (box_a[0][0] + box_a[1][0]) >= (box_b[0][0] + box_b[1][0]) else 'LEFT'


def save_position(box_a, box_b, rotation):
    """Posição relativa de A a B: distância do canto mínimo de A ao canto de B do mesmo lado, mais a rotação."""
    side = side_of(box_a, box_b)
    anchor_x = box_b[1][0] if side == 'RIGHT' else box_b[0][0]
    ref_x = box_a[0][0] if side == 'RIGHT' else box_a[1][0]
    return {'delta': (ref_x - anchor_x, box_a[0][1] - box_b[0][1], box_a[0][2] - box_b[0][2]),
            'rotation': float(rotation), 'b_side': side}


def apply_position(saved, box_a, box_b):
    """Deslocamento a somar em A (já com a rotação salva aplicada à caixa) para repetir a posição salva."""
    dx, dy, dz = saved['delta']
    if saved['b_side'] == 'RIGHT':
        target_x, current_x = box_b[1][0] + dx, box_a[0][0]
    else:
        target_x, current_x = box_b[0][0] + dx, box_a[1][0]
    return (target_x - current_x, box_b[0][1] + dy - box_a[0][1], box_b[0][2] + dz - box_a[0][2])
