# Regression watch — 001-addon-moveis-planejados

> Criado por `/reversa-coding` em 2026-10-01 (incremento 1). Cada item é conferido pelo agente reverso na próxima
> execução de `/reversa`, contra os artefatos regenerados em `_reversa_sdd/`.

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/hb_placement/requirements.md`, RN-05 | O parser de medidas digitadas NÃO aceita frações (`a/b`, `a b/c`) nem pés/polegadas (`'`, `"`, `in`, `ft`) | ausência | Spec regenerada volta a descrever frações ou notação imperial no parser de `hb_placement.py` |
| W002 | `_reversa_sdd/hb_placement/requirements.md`, RN-06 | Número sem sufixo é interpretado na unidade `btm_settings.btm_unit`; vírgula e ponto são aceitos como decimal | redação | Spec diz que o número puro segue só `unit_settings.length_unit` ou ignora a vírgula decimal |
| W003 | `_reversa_sdd/hb_core/requirements.md`, RN-18 | `Unit Type` da cota usa `btm_settings.btm_unit` (MM=2, CM=3, M=4) antes de `unit_settings`; trocar a unidade reaplica em todas as cotas | redação | Spec descreve `Unit Type` apenas por `unit_settings` ou sem atualização na troca de unidade |
| W004 | `_reversa_sdd/hb_core/requirements.md`, objetivo "inputs GN pelo nome" | Leitura/escrita de inputs GN existe em um só lugar (`compat.py`), com cache por `session_uid`; `hb_utils`/`hb_types` só reexportam | presença | Spec aponta implementações duplicadas em `hb_utils.py`/`hb_types.py` ou acesso `mod["Socket_X"]` |
| W005 | `_reversa_sdd/cutting/requirements.md`, agrupamento em `nesting.py` | Chapas separadas por matéria-prima, espessura **e acabamento** (`finish`) | redação | Spec descreve agrupamento só por material e espessura |
| W006 | `_reversa_sdd/cutting/requirements.md`, `NestingPart` / exportação | Exportação gera JSON `schema_version` 2.0.0 (`parts`, `materials`, `modules`, `cut_plan`); v1 só na importação (convertido) | redação | Spec descreve `parts_catalog`/`schema_version 1.0.0` como saída atual |
| W007 | `_reversa_sdd/cutting/requirements.md`, extração de peças | Gabinetes frameless/closets geram peças a partir dos `GeoNodeCutpart` visíveis, com `uid = <btm_uid>/<componente>/<índice>` estável; sintético só para módulos `btm_*` | presença | Spec volta a descrever peças deduzidas das medidas do módulo para todos os gabinetes |
| W008 | `_reversa_sdd/frameless/requirements.md`, dívida "Undo" (`ops_defaults.py`) | Operadores de propagação de padrões do frameless têm `UNDO` e aceitam pular medidas manuais (`btm_overrides`) | redação | Spec regenerada volta a listar `ops_defaults.py` sem `UNDO` ou sem o filtro de medidas manuais |

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso em cada `/reversa` futuro: data, veredito 🟢/🟡/🔴 por item. -->

## Arquivadas

<!-- Itens que deixaram de ser relevantes, com data e motivo. -->

## Observações

Itens sem peso de regressão (regras de origem 🟡/🔴 ou decisões novas desta feature):

- Mapeamento de papéis de peça → componente (`cutting/part_roles.py`: `Top` → `BAS`, fundo por tipo de gabinete,
  cabideiro e caixa de gaveta fora da lista de corte) é decisão 🟡 do roadmap (D-09).
- Comparação do limite de chapa por medidas ordenadas (lado maior × maior limite) é decisão 🟡 (D-12).
- `btm_overrides` só é gravado quando o valor difere do padrão da cena (closets) ou do valor inicial do diálogo
  (frameless); edições por drivers ou scripts não são marcadas. 🟡
