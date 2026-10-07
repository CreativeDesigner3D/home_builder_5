"""Agregado como peça de produção (feature 003, T046; RN-13, D-15).

Marcado, o agregado entra no plano de corte como uma placa com as medidas da caixa dele (maior, média e menor
medida), pelo mesmo caminho das geometrias livres (`cutting/part_sources.geometry_records`), com matéria-prima e
componente de `btm_geometry`. A malha do agregado não é alterada.
"""


def sync(obj):
    geometry = getattr(obj, 'btm_geometry', None)
    if geometry is None:
        return
    geometry.fabrication = bool(obj.btm_aggregate.production_part)


def sheet(obj):
    """(nome, comprimento, largura, espessura) em metros, ou None se não for peça de produção."""
    agg = obj.btm_aggregate
    if not (agg.is_aggregate and agg.production_part):
        return None
    a, b, c = sorted((abs(v) for v in agg.size), reverse=True)
    return obj.name, a, b, c
