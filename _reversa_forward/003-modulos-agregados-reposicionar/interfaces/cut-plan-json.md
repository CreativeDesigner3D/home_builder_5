# Contrato: JSON de produção (`caffmob_draw.project`)

> Feature: `003-modulos-agregados-reposicionar` · Decisões D-14, D-15 · Arquivo: `caffmob_draw/cutting/json_exporter.py`

## Mudança

Versão `2.0.0` → **`2.1.0`** (menor, compatível). Cada peça (`parts[]`) ganha o campo opcional `machining`, uma
lista de recortes vindos de agregados com "Furo real no plano de corte" marcado. `drilling` continua `[]`.

```json
{
  "uid": "a1b2/LATERAL/0",
  "...": "campos de 2.0.0 sem mudança",
  "drilling": [],
  "machining": [
    {
      "kind": "POCKET",
      "source": "AGGREGATE",
      "source_name": "Nicho importado",
      "face": "TOP",
      "x_mm": 120.0, "y_mm": 300.0,
      "end_x_mm": 520.0, "end_y_mm": 700.0,
      "depth_mm": 10.0,
      "through": false
    }
  ]
}
```

| Campo | Tipo | Regra |
|---|---|---|
| `kind` | `"POCKET"` \| `"THROUGH_CUT"` | `THROUGH_CUT` quando `depth_mm` ≥ espessura da peça |
| `source` | `"AGGREGATE"` | Só recortes de agregados nesta versão; recortes de sistema (`CPM_CUTOUT` de LED, rasgo) ficam fora |
| `source_name` | string | Nome do objeto agregado |
| `face` | `"TOP"` \| `"BOTTOM"` | Face da peça por onde o recorte entra (`Flip Z` do `CPM_CUTOUT`) |
| `x_mm`, `y_mm`, `end_x_mm`, `end_y_mm` | número | Retângulo no referencial da peça (comprimento × largura), mesma precisão de `length_mm` |
| `depth_mm` | número | `Route Depth` do `CPM_CUTOUT`, ≤ `thickness_mm` |
| `through` | bool | Igual a `kind == "THROUGH_CUT"` (atalho para leitores simples) |

## Compatibilidade

- Leitor (`validate`): aceita `2.0.0` e `2.1.0` (`SUPPORTED_MAJOR = 2`, sem mudança); `machining` ausente = lista vazia.
- Peças sem agregado com furo real: `machining` sai como `[]` (o arquivo gerado continua válido para leitores 2.0).
- Formatos antigos aceitos (`ACCEPTED_FORMATS`, BUG-20261006-QAVK) sem mudança.

## Erros

- Recorte fora da peça (retângulo além de `length_mm`/`width_mm`): recortado ao contorno e registrado em
  `limit_status` da peça como `"MACHINING_CLIPPED"`.
- Agregado cujo pai não é `GeoNodeCutpart`: não gera `machining` (a opção já fica desabilitada na UI).

## Idempotência

Exportar duas vezes o mesmo projeto gera listas idênticas, ordenadas por `source_name` e depois por `x_mm`, `y_mm`.
