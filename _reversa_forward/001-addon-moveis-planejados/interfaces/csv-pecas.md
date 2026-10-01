# Contrato: CSV genérico de peças

> Feature `001-addon-moveis-planejados` · Requisito RF-113a (clarify C-5).

## Finalidade

Levar a lista de peças a planilhas e otimizadores de corte que não leem o JSON global v2.

## Formato

- Codificação UTF-8 com BOM (para abrir corretamente em planilhas), fim de linha `\r\n`.
- Separador de campos `;`, vírgula decimal, valores em **mm** com 1 casa decimal.
- Uma linha de cabeçalho; uma linha por peça (quantidade na coluna `quantidade`, sem repetir linhas).
- Texto com `;`, aspas ou quebra de linha entre aspas duplas (aspas internas duplicadas).

## Colunas (nesta ordem)

| Coluna | Conteúdo |
|---|---|
| `id` | `uid` estável da peça (igual ao JSON v2) |
| `modulo` | Nome do módulo |
| `modulo_id` | `btm_uid` do módulo |
| `peca` | Nome da peça |
| `componente` | Código do componente (`LAT`, `BAS`…) |
| `comprimento` | mm |
| `largura` | mm |
| `espessura` | mm |
| `quantidade` | inteiro |
| `materia_prima` | Ex.: MDF |
| `acabamento` | Ex.: Branco, Cinza Fóssil |
| `fita_1` .. `fita_4` | Espessura da fita em mm (0 = sem fita); 1–2 = bordas do comprimento, 3–4 = bordas da largura |
| `veio` | `NENHUM` / `COMPRIMENTO` / `LARGURA` |
| `situacao` | `OK` / `EXCEDE_LARGURA` / `EXCEDE_COMPRIMENTO` |

## Regras

- Ordem das linhas por `modulo_id` e `id` (saída idempotente).
- Escrita atômica; arquivo só exportado (sem importação no incremento 1).
