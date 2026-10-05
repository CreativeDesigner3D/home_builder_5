"""Folha 3D das portas de ambiente — matemática pura, sem `bpy` (T041; D-20).

O Home Builder 5 desenha a porta de ambiente como uma gaiola de recorte (`Dim X` = largura, `Dim Y` = espessura da
parede, `Dim Z` = altura) e um símbolo 2D (`GeoNodeDoorSwing`). Medido no Blender 5.2 (porta 0,90 × parede 0,15):
- "Swing Inside": dobradiça em y = `Dim Y` e o arco vai para −Y; sem ele, dobradiça em y = 0 e o arco vai para +Y;
- porta simples: `Is Left` põe a dobradiça em x = largura; sem `Is Left`, em x = 0;
- porta dupla: duas folhas de meia largura, com dobradiças em x = 0 e x = largura.

Cada `Leaf` está no referencial local da porta. A caixa da folha fechada, no referencial do pivô (na dobradiça), vai de
x = 0 a `dx·length`, de y = 0 a `dy·thickness` e de z = 0 a `height`. Abrir `a` graus = girar o pivô em Z por
`rot_sign·a`.
"""

import math
from collections import namedtuple

Leaf = namedtuple('Leaf', 'side hinge_x hinge_y dx dy length thickness height rot_sign')


def leaves(width, wall_depth, height, is_left, is_double, swing_inside, door_thickness):
    """Folhas da porta (uma ou duas), na ordem esquerda → direita."""
    sign = -1.0 if swing_inside else 1.0          # lado para onde a folha abre (Y local da porta)
    hinge_y = wall_depth if swing_inside else 0.0
    dy = -sign                                     # a espessura da folha fechada fica do lado oposto ao giro
    if is_double:
        hinges = (('L', 0.0, 1.0), ('R', width, -1.0))
        length = width / 2.0
    else:
        hinges = (('R', width, -1.0),) if is_left else (('L', 0.0, 1.0),)
        length = width
    return [Leaf(side, x, hinge_y, dx, dy, length, door_thickness, height, sign * dx) for side, x, dx in hinges]


def leaf_corners(leaf):
    """Os 8 cantos da caixa da folha fechada, no referencial do pivô."""
    xs = (0.0, leaf.dx * leaf.length)
    ys = (0.0, leaf.dy * leaf.thickness)
    zs = (0.0, leaf.height)
    return [(x, y, z) for x in xs for y in ys for z in zs]


def open_tip(leaf, degrees):
    """Ponta livre da folha (no nível do piso), em coordenadas locais da porta, com a folha aberta `degrees`."""
    a = math.radians(leaf.rot_sign * degrees)
    x, y = leaf.dx * leaf.length, 0.0
    return (leaf.hinge_x + x * math.cos(a) - y * math.sin(a), leaf.hinge_y + x * math.sin(a) + y * math.cos(a))
