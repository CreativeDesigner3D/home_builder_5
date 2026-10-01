"""CSV genérico de peças (T027; RF-113a, clarify C-5).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/csv-pecas.md`.
UTF-8 com BOM, separador `;`, vírgula decimal, valores em mm com 1 casa, uma linha por peça. Python puro.
"""

import csv
import io
import os
import tempfile

CSV_COLUMNS = (
    "id", "modulo", "modulo_id", "peca", "componente", "comprimento", "largura", "espessura", "quantidade",
    "materia_prima", "acabamento", "fita_1", "fita_2", "fita_3", "fita_4", "veio", "situacao",
)

GRAIN_LABELS = {'NONE': "NENHUM", 'VERTICAL': "COMPRIMENTO", 'HORIZONTAL': "LARGURA"}
STATUS_LABELS = {'OK': "OK", 'EXCEEDS_WIDTH': "EXCEDE_LARGURA", 'EXCEEDS_LENGTH': "EXCEDE_COMPRIMENTO"}


def format_mm(value, precision=1):
    """Número em mm com vírgula decimal, sem zeros à direita (`720`, `0,4`, `18,5`)."""
    text = f"{round(float(value or 0.0), precision):.{precision}f}"
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    if text in ("-0", ""):
        text = "0"
    return text.replace('.', ',')


def part_rows(parts):
    """Linhas (dict coluna → texto) em ordem estável: por `modulo_id` e depois `id`."""
    rows = []
    for part in parts:
        edges = list(part.edges)
        rows.append({
            "id": part.uid,
            "modulo": part.module_ref or "",
            "modulo_id": part.module_uid or "",
            "peca": part.name,
            "componente": part.component,
            "comprimento": format_mm(part.height),
            "largura": format_mm(part.width),
            "espessura": format_mm(part.thickness),
            "quantidade": str(int(part.quantity)),
            "materia_prima": part.material or "",
            "acabamento": part.finish or "",
            "fita_1": format_mm(edges[0]),
            "fita_2": format_mm(edges[1]),
            "fita_3": format_mm(edges[2]),
            "fita_4": format_mm(edges[3]),
            "veio": GRAIN_LABELS.get(part.grain_direction, "NENHUM"),
            "situacao": STATUS_LABELS.get(part.limit_status, part.limit_status),
        })
    rows.sort(key=lambda r: (r["modulo_id"], r["id"]))
    return rows


def parts_csv_text(parts):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, delimiter=';', lineterminator='\r\n',
                            quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(part_rows(parts))
    return buffer.getvalue()


def write_parts_csv(path, parts):
    """Grava o CSV (escrita atômica). Devolve o número de linhas de peça."""
    text = parts_csv_text(parts)
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as handle:
            handle.write(text)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return len(parts)
