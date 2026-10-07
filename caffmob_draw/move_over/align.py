"""Alinhamento do "Mover Sobre" (T004; RN-05 a RN-08). Python puro, sem `bpy`.

Tudo no referencial de B (o objeto de referência), em metros:
- X: largura (esquerda → direita);
- Y: profundidade, com a **frente em Y mínimo** (todas as bibliotecas e o módulo rápido têm a frente em −Y e o fundo em
  Y ≈ 0); "profundidade 0%" = frente de B, "100%" = fundo de B;
- Z: altura.

Caixas são `((xmin, ymin, zmin), (xmax, ymax, zmax))`. Os alvos têm um tipo e, para alinhar, um valor:
- `LEFT` / `RIGHT`: A encostado do lado esquerdo/direito de B;
- `DEPTH` (fração): face frontal de A na profundidade de B;
- `HEIGHT` (fração): base de A na altura de B;
- `STACK`: A empilhado sobre B;
- `WALL_FACE`: com uma parede como B, o fundo de A na face da parede.
"""

from collections import namedtuple

FRACTIONS = (0.0, 0.30, 0.50, 0.75, 1.0)
DEFAULT_TOLERANCE_PX = 12.0

Target = namedtuple('Target', 'kind value')
LEFT, RIGHT, DEPTH, HEIGHT, STACK, WALL_FACE = 'LEFT', 'RIGHT', 'DEPTH', 'HEIGHT', 'STACK', 'WALL_FACE'


def size(box):
    return tuple(box[1][i] - box[0][i] for i in range(3))


def translate(box, delta):
    return (tuple(box[0][i] + delta[i] for i in range(3)), tuple(box[1][i] + delta[i] for i in range(3)))


def delta_for(target, box_a, box_b, wall=False):
    """Deslocamento (dx, dy, dz) que leva A ao alvo. Eixos não afetados ficam em 0."""
    (ax0, ay0, az0), (ax1, ay1, az1) = box_a
    (bx0, by0, bz0), (bx1, by1, bz1) = box_b
    if target.kind == LEFT:
        return (bx0 - ax1, 0.0, 0.0)
    if target.kind == RIGHT:
        return (bx1 - ax0, 0.0, 0.0)
    if target.kind == DEPTH:
        plane = by0 + target.value * (by1 - by0)
        return (0.0, plane - ay0, 0.0)
    if target.kind == WALL_FACE:
        return (0.0, by0 - ay1, 0.0)          # fundo de A na face da parede (frente da parede em Y mínimo)
    if target.kind == HEIGHT:
        return (0.0, 0.0, bz0 + target.value * (bz1 - bz0) - az0)
    if target.kind == STACK:
        return (0.0, 0.0, bz1 - az0)
    raise ValueError(f"Alvo desconhecido: {target.kind}")


def combine(targets, box_a, box_b, wall=False):
    """Soma os deslocamentos de alvos em eixos diferentes (ex.: lado + profundidade)."""
    total = [0.0, 0.0, 0.0]
    for target in targets:
        d = delta_for(target, box_a, box_b, wall)
        for i in range(3):
            if d[i]:
                total[i] = d[i]
    return tuple(total)


# Alvos em cada vista --------------------------------------------------------------------------------------
# Vista superior: eixo horizontal da tela = X, vertical = Y (frente embaixo).
# Vista frontal: eixo horizontal = X, vertical = Z.

def top_view_lines(box_b, wall=False):
    """[(Target, ((x0,y0),(x1,y1)))] — segmentos dos alvos na vista superior, em coordenadas do mundo 2D."""
    (bx0, by0, _), (bx1, by1, _) = box_b
    lines = [(Target(LEFT, None), ((bx0, by0), (bx0, by1))), (Target(RIGHT, None), ((bx1, by0), (bx1, by1)))]
    if wall:
        lines.append((Target(WALL_FACE, None), ((bx0, by0), (bx1, by0))))
        return lines
    for fraction in FRACTIONS:
        y = by0 + fraction * (by1 - by0)
        lines.append((Target(DEPTH, fraction), ((bx0, y), (bx1, y))))
    return lines


def front_view_lines(box_b):
    (bx0, _, bz0), (bx1, _, bz1) = box_b
    lines = [(Target(LEFT, None), ((bx0, bz0), (bx0, bz1))), (Target(RIGHT, None), ((bx1, bz0), (bx1, bz1)))]
    for fraction in FRACTIONS:
        z = bz0 + fraction * (bz1 - bz0)
        lines.append((Target(HEIGHT, fraction), ((bx0, z), (bx1, z))))
    return lines


def pick(click_px, lines_px, tolerance_px=DEFAULT_TOLERANCE_PX):
    """Alvos atingidos por um clique: no máximo um por eixo (lado e profundidade/altura podem se combinar).

    `lines_px` = [(Target, (p0_px, p1_px))] já na tela. Devolve a lista de Targets escolhidos.
    """
    from ..canvas2d.view import distance_point_segment
    best = {}
    for target, (p0, p1) in lines_px:
        dist = distance_point_segment(click_px, p0, p1)
        if dist > tolerance_px:
            continue
        axis = 'x' if target.kind in (LEFT, RIGHT) else 'v'
        if axis not in best or dist < best[axis][0]:
            best[axis] = (dist, target)
    return [t for _d, t in best.values()]


def pick_stack(click_px, top_line_px, tolerance_px=DEFAULT_TOLERANCE_PX):
    """Na vista frontal, clique acima do topo de B (dentro da largura de B e além da tolerância) = empilhar."""
    (x0, y0), (x1, _y1) = top_line_px
    lo, hi = min(x0, x1), max(x0, x1)
    return lo <= click_px[0] <= hi and click_px[1] > y0 + tolerance_px


def gaps(box_a, box_b):
    """Distâncias entre A e B para mostrar na janela: (X, profundidade, altura), positivas quando separados.

    X: entre as faces mais próximas; profundidade: frente de A − frente de B; altura: base de A − base de B.
    """
    (ax0, ay0, az0), (ax1, _ay1, _az1) = box_a
    (bx0, by0, bz0), (bx1, _by1, _bz1) = box_b
    if ax0 >= bx1:
        dx = ax0 - bx1
    elif bx0 >= ax1:
        dx = bx0 - ax1
    else:
        dx = -min(ax1 - bx0, bx1 - ax0)   # sobrepostos em X
    return dx, ay0 - by0, az0 - bz0


def overlaps(box_a, box_b, tolerance=1e-4):
    return all(box_a[0][i] < box_b[1][i] - tolerance and box_b[0][i] < box_a[1][i] - tolerance for i in range(3))
