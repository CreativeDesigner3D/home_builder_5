"""Contorno do piso pela face interna das paredes (BUG-20261007-A2G7). Python puro, sem `bpy`.

Substitui, no "Ajustar Piso", o fecho convexo dos vértices das paredes (que cobria o recorte de salas em L/U e passava
pela face externa):
- laço do Home Builder 5: as origens das paredes em sequência, com a espessura à esquerda do sentido (+Y local); se a
  espessura cai para dentro do laço, a face interna fica uma espessura para dentro;
- paredes da camada nova (`btm_wall_segments`): a linha de centro vira face interna pelas cadeias do editor 2D
  (`walls2d.convert`);
- sem sala fechada: retângulo pelas pontas das paredes.
Os polígonos saem em ordem anti-horária (face para cima).
"""

from ..walls2d import convert, model


def area(points):
    """Área com sinal (positiva no anti-horário)."""
    total = 0.0
    for i, (x0, y0) in enumerate(points):
        x1, y1 = points[(i + 1) % len(points)]
        total += x0 * y1 - x1 * y0
    return total / 2.0


def is_ccw(points):
    return area(points) > 0.0


def ccw(points):
    points = [tuple(map(float, p[:2])) for p in points]
    return points if is_ccw(points) else points[::-1]


def hb_loop_inner(points, thicknesses):
    """Face interna de um laço fechado de paredes do Home Builder 5 (origens em sequência, espessura em +Y)."""
    segments = [model.Segment(thickness=float(t), height=2.6) for t in thicknesses]
    chain = model.Chain(points, segments, closed=True, side='LEFT')
    if chain.outward_side() == 'LEFT':          # espessura para fora: as origens já são a face interna
        return ccw(chain.nodes)
    return ccw(chain.shifted_nodes(1.0))        # espessura para dentro: uma espessura para a esquerda


def segments_inner_loops(segments):
    """Faces internas das cadeias fechadas de trechos da camada nova ({'start', 'end', 'thickness', ...} no mundo)."""
    return [ccw(chain.nodes) for chain in convert.chains_from_segments(segments) if chain.closed]


def bounding_rect(points):
    points = [tuple(map(float, p[:2])) for p in points]
    if not points:
        return None
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
