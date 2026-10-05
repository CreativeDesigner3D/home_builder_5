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
| W009 | `_reversa_sdd/data-dictionary-legacy.md`, `hb_door_open / hb_drawer_open` | Estado de abertura das frentes do closets é **fração 0–1** (float); valores inteiros 0/1 de arquivos antigos continuam válidos | redação | Spec regenerada descreve o campo como `int` 0/1 |
| W010 | `_reversa_sdd/data-dictionary.md`, `collision_global` | Propriedade exibida como "Evitar Sobreposição" (RN-13) | redação | Spec volta a chamar o campo de "Colisões Globais" ou "Evitar Colisões Físicas" |
| W011 | `_reversa_sdd/frameless/requirements.md`, frentes (`types_frameless.py` `CabinetDoor`/`CabinetFlipUpDoor`/`CabinetDrawerFront`/`CabinetPulloutFront`) | Frentes frameless abrem por `delta_rotation_euler`/`delta_location` (idprop `btm_open`) sem alterar drivers de medida nem a hierarquia | presença | Spec não menciona abertura de frentes no frameless ou descreve pivôs/drivers novos para isso |
| W012 | `_reversa_sdd/hb_core` (handlers de aplicação) | `save_pre` fecha as frentes abertas e `save_post`/`save_post_fail` reabrem; com `btm_settings.save_fronts_open` nada muda (RN-14) | presença | Spec regenerada não lista os handlers de salvar ou diz que o arquivo guarda as frentes abertas |
| W013 | `_reversa_sdd/hb_placement/requirements.md`, RN-09 | Filhos-módulo da parede só são obstáculos com `btm_settings.collision_global` ("Evitar Sobreposição") ligado; portas/janelas e linhas de encaixe sempre | redação | Spec regenerada descreve todos os filhos como obstáculos sem condição |
| W014 | `_reversa_sdd/hb_placement/requirements.md`, RN-14 | Gabinetes livres e intrusões de paredes adjacentes/em T só bloqueiam com "Evitar Sobreposição" ligado | redação | Spec descreve gabinetes livres ou intrusões como obstáculos incondicionais |
| W015 | `_reversa_sdd/face_frame/` e `_reversa_sdd/closets/` (modos de abrir) | `hb_face_frame.open_mode` e `hb_closets.open_door_mode` apenas abrem `btm.inspect_fronts`; não têm animação própria | presença | Spec volta a descrever tween/estado próprios nesses operadores ou estado 0/1 gravado por eles |

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
- (incremento 3) Posição fechada do controlador do módulo rápido em Y = 0 (`geometry/door_controller.py`); a regra
  anterior (0,03 m) não constava como 🟢 nas specs. 🟡
- (incremento 3) Teto comum de 90° para as frentes articuladas de todas as linhas, convertido para os máximos legados
  (face frame 100°, closets 110°) — decisão D-20 🟡.
- (incremento 3) Envelope de interferência por cascos convexos de poses a cada 15° com tolerância de 1 mm — D-29 🟡.
- (incremento 3) Abrir portas não marca o plano de corte como desatualizado (`cutting/stale.py`, regra criada no
  incremento 1, sem origem 🟢 nas specs do legado) — D-31.
