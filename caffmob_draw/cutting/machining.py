"""Usinagem de peças vinda de agregados com "Furo real no plano de corte" (feature 003, T045; D-14). Python puro.

Contrato: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/cut-plan-json.md`.
Entrada: recortes `CPM_CUTOUT` lidos da peça, em metros no referencial da peça (X ao longo do comprimento,
Y ao longo da largura). Saída: entradas `machining` em milímetros.
"""

AGGREGATE_PREFIX = "Agregado: "
CLIPPED_STATUS = "MACHINING_CLIPPED"


def _mm(value, precision):
    return round(float(value) * 1000.0, precision)


def entries(cutouts, length, width, thickness, precision=1):
    """(lista de entradas, recortado?) — recortes fora da peça são cortados ao contorno."""
    out, clipped = [], False
    for cut in cutouts:
        x0, x1 = sorted((float(cut['x']), float(cut['end_x'])))
        y0, y1 = sorted((float(cut['y']), float(cut['end_y'])))
        cx0, cx1 = max(0.0, x0), min(float(length), x1)
        cy0, cy1 = max(0.0, y0), min(float(width), y1)
        if (cx0, cx1, cy0, cy1) != (x0, x1, y0, y1):
            clipped = True
        if cx1 - cx0 <= 1e-9 or cy1 - cy0 <= 1e-9:
            continue
        depth = min(float(cut['depth']), float(thickness))
        through = depth >= float(thickness) - 1e-6
        out.append({
            "kind": "THROUGH_CUT" if through else "POCKET",
            "source": "AGGREGATE",
            "source_name": str(cut['name']),
            "face": "BOTTOM" if cut.get('flip_z') else "TOP",
            "x_mm": _mm(cx0, precision), "y_mm": _mm(cy0, precision),
            "end_x_mm": _mm(cx1, precision), "end_y_mm": _mm(cy1, precision),
            "depth_mm": _mm(depth, precision),
            "through": through,
        })
    out.sort(key=lambda e: (e["source_name"], e["x_mm"], e["y_mm"]))
    return out, clipped


def source_name(modifier_name):
    """Nome do agregado a partir do nome do modificador (`"Agregado: <nome>"`), ou None se não for de agregado."""
    if modifier_name.startswith(AGGREGATE_PREFIX):
        return modifier_name[len(AGGREGATE_PREFIX):]
    return None
