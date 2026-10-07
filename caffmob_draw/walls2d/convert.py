"""Conversão das paredes da camada nova para o modelo do editor — Python puro (T042; D-22, RF-38).

O `caffmob.wall_builder` grava em `obj["btm_wall_segments"]` a linha de centro de cada trecho (`start`, `end`),
`thickness` e `height`. Aqui os trechos (já no mundo) viram cadeias do modelo: trechos cuja ponta coincide (até
`JOIN_TOLERANCE`) com o início de outro ficam na mesma cadeia, em qualquer ordem de entrada; a cadeia fecha quando o fim
volta ao início. Como os nós do modelo são a face interna (D-25, D-26), a linha de centro é deslocada meia espessura
para o lado oposto à espessura: contorno fechado → Direção para fora; cadeia aberta → Direção esquerda. As cadeias saem
como trechos **novos** (sem `source`) e a parede convertida fica no mesmo lugar.
"""

import math

from . import model

JOIN_TOLERANCE = 0.01


def _close(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) <= JOIN_TOLERANCE


def chains_from_segments(segments):
    """[`model.Chain`] a partir de [{'start': (x, y), 'end': (x, y), 'thickness': t, 'height': h}]."""
    pending = [s for s in segments if math.hypot(s['end'][0] - s['start'][0], s['end'][1] - s['start'][1]) > 1e-6]
    chains = []
    while pending:
        run = [pending.pop(0)]
        grown = True
        while grown:                        # cresce pelas duas pontas
            grown = False
            for seg in list(pending):
                if _close(run[-1]['end'], seg['start']):
                    run.append(seg)
                elif _close(seg['end'], run[0]['start']):
                    run.insert(0, seg)
                else:
                    continue
                pending.remove(seg)
                grown = True
        closed = len(run) >= 3 and _close(run[-1]['end'], run[0]['start'])
        nodes = [tuple(map(float, s['start'][:2])) for s in run]
        if not closed:
            nodes.append(tuple(map(float, run[-1]['end'][:2])))
        segs = [model.Segment(thickness=float(s['thickness']), height=float(s.get('height', 2.6))) for s in run]
        center = model.Chain(nodes, segs, closed=closed, side='LEFT')
        side = center.outward_side() if closed else 'LEFT'
        inner = center.shifted_nodes(0.5 if side == 'RIGHT' else -0.5)   # meia espessura, longe do lado da espessura
        chains.append(model.Chain(inner, segs, closed=closed, side=side))
    return chains
