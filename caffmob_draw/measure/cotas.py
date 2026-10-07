"""Cotas de um módulo na parede (T005; RN-04, D-11). Python puro, sem `bpy`.

Tudo no referencial da parede, em metros: X ao longo da parede (0 = início, `wall_length` = fim), Z = altura a partir
do piso, Y = profundidade com a face da parede em Y = 0 e os módulos do lado da frente em Y < 0.

- Módulo: `x0`, largura, `z0`, altura, `back_y` (Y do fundo do módulo).
- Obstáculos: intervalos `(x0, x1, z0, z1)` de outros itens da parede (módulos, portas, janelas).
"""

from collections import namedtuple

Cotas = namedtuple('Cotas', 'afastamento anterior posterior inferior superior')
Placement = namedtuple('Placement', 'x0 width z0 height back_y')

FIELDS = ('afastamento', 'anterior', 'posterior', 'inferior', 'superior')
LABELS = {'afastamento': "Afastamento da parede", 'anterior': "Cota anterior", 'posterior': "Cota posterior",
          'inferior': "Cota inferior", 'superior': "Cota superior"}


def _vertical_overlap(z0, z1, oz0, oz1):
    return z0 < oz1 and oz0 < z1   # sobreposição estrita (hb_placement RN-12)


def limits(placement, obstacles, wall_length):
    """(limite à esquerda, limite à direita) do módulo: obstáculo vizinho na mesma faixa de altura ou fim da parede."""
    x0, x1 = placement.x0, placement.x0 + placement.width
    z0, z1 = placement.z0, placement.z0 + placement.height
    left, right = 0.0, wall_length
    for ox0, ox1, oz0, oz1 in obstacles:
        if not _vertical_overlap(z0, z1, oz0, oz1):
            continue
        if ox1 <= x0 + 1e-9:
            left = max(left, ox1)
        elif ox0 >= x1 - 1e-9:
            right = min(right, ox0)
    return left, right


def compute(placement, obstacles, wall_length, ceiling_height):
    left, right = limits(placement, obstacles, wall_length)
    return Cotas(
        afastamento=-placement.back_y,
        anterior=placement.x0 - left,
        posterior=right - (placement.x0 + placement.width),
        inferior=placement.z0,
        superior=ceiling_height - (placement.z0 + placement.height),
    )


def compute_free(placement, ceiling_height):
    """Módulo sem parede: só cotas verticais (anterior, posterior e afastamento ficam None)."""
    return Cotas(None, None, None, placement.z0, ceiling_height - (placement.z0 + placement.height))


def apply(field, value, placement, obstacles, wall_length, ceiling_height):
    """Nova `Placement` com a cota `field` = `value`, mantendo as dimensões (RN-04).

    Levanta ValueError com mensagem "Valor Inválido" para valor negativo ou que tire o módulo da parede.
    """
    if value < 0:
        raise ValueError(f"Valor Inválido: {LABELS[field]} não pode ser negativa.")
    p = placement
    if field == 'afastamento':
        return p._replace(back_y=-value)
    if field == 'inferior':
        return p._replace(z0=value)
    if field == 'superior':
        z0 = ceiling_height - value - p.height
        if z0 < 0:
            raise ValueError(f"Valor Inválido: {LABELS[field]} maior que o espaço até o piso.")
        return p._replace(z0=z0)
    left, right = limits(p, obstacles, wall_length)
    if field == 'anterior':
        x0 = left + value
    elif field == 'posterior':
        x0 = right - value - p.width
    else:
        raise ValueError(f"Cota desconhecida: {field}")
    if x0 < 0 or x0 + p.width > wall_length + 1e-9:
        raise ValueError(f"Valor Inválido: {LABELS[field]} tira o módulo da parede.")
    return p._replace(x0=x0)


def slide(placement, obstacles, wall_length, target_x0, avoid=True):
    """`x0` do módulo arrastado ao longo da parede até `target_x0` (RF-34).

    Com "Evitar Sobreposição", para no primeiro obstáculo da mesma faixa de altura e no começo/fim da parede; sem,
    só fica dentro da parede.
    """
    if not avoid:
        return min(max(target_x0, 0.0), max(0.0, wall_length - placement.width))
    left, right = limits(placement, obstacles, wall_length)
    return min(max(target_x0, left), max(left, right - placement.width))
