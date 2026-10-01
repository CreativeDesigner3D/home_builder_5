# closets — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Caminhos relativos a `blendertomob/product_libraries/closets/`.

## Pré-requisitos
- [ ] [`hb_core`](../hb_core/tasks.md) (ponte GN por nome), [`hb_placement`](../hb_placement/tasks.md) (com
      `PlacementDimSpec` sem reordenar campos e `duplicate_object_hierarchy` — decisão PL-06).
- [ ] **Preset BR** (padrão) / EUA definido (`product_common` Q-06): espessuras, profundidade, vão máximo, alturas.
- [ ] Interfaces de `GeoNodeClosetRod`, `CPM_5PIECEDOOR`, `CPM_CORNERNOTCH` em
      [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md).
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`.

## Tarefas

### Bloco A — Dados e registro

- [ ] T-01, `Closet_Starter_Props`, `Closet_Bay_Props`, `Closets_Scene_Props` com padrões do preset (BR: chapa 15/18 mm, profundidade 550–600 mm)
  - Origem no legado: `props_closets.py:106-372`; `const_closets.py:13-140`
  - Critério de pronto: trocar o preset muda os padrões; preset EUA reproduz 0,75"/14"/80"
  - Confiança: 🟢 (estrutura) / 🟡 (valores BR, Q-01)

- [ ] T-02, Idprops de configuração encapsulados num acessor tipado (leitura/escrita validada) sem mudar o armazenamento
  - Origem no legado: `types_closets.py:52-100`
  - Critério de pronto: nenhum `obj['hb_*']` espalhado fora do acessor; valores inválidos rejeitados
  - Confiança: 🟢

- [ ] T-03, `register()`/`unregister()` sem engolir exceções; remover timer do Open Door, handlers e keymaps; limpar `_drag_op` em `load_post`
  - Origem no legado: `closets/__init__.py:10-21`; `op_open_door_closet.py:92-100, 223-230`; `op_grab_closet.py:55-59, 386-391, 892-898`; `ops_closet.py:2881-2902`
  - Critério de pronto: registrar/desregistrar 2× sem resíduo, inclusive com grab/open door ativos
  - Confiança: 🟢

- [ ] T-04, `closet_type` com valores para ilha dupla e L-shelf
  - Origem no legado: `props_closets.py:121-129`; `types_closets.py:1529-1531`
  - Critério de pronto: cada classe grava seu próprio tipo
  - Confiança: 🟡 (Q-08)

### Bloco B — Solver e recálculo

- [ ] T-05, `distribute_widths` / `compute_layout` puros, com aviso quando o vão livre fica abaixo do mínimo
  - Origem no legado: `solver_closets.py:26-126`
  - Critério de pronto: cenários do solver de `requirements.md`; soma não fechada gera aviso
  - Confiança: 🟢

- [ ] T-06, `ClosetStarter.recalculate` com propagação por `hb_last_height/depth` e guardas por chave estável
  - Origem no legado: `types_closets.py:105-106`, `:458-521`
  - Critério de pronto: RN-06; guarda por `as_pointer()` ou nome
  - Confiança: 🟢

- [ ] T-07, Layout de painéis, vãos, prateleiras, rodapé, cleat, trilho, fundos e pontes
  - Origem no legado: `types_closets.py:523-689`, `:1244-1339`
  - Critério de pronto: RN-04, RN-05, RN-12..RN-14
  - Confiança: 🟢

- [ ] T-08, Fundo configurável: aplicado (legado) ou fino encaixado; cleat opcional
  - Origem no legado: `types_closets.py:363-367`, `:576-584`, `:623-651`
  - Critério de pronto: preset BR gera fundo de 6 mm encaixado com recuo
  - Confiança: 🟡 (Q-04)

- [ ] T-09, Prateleiras divisoras e segmentos (A2), com a distinção fixa (divide o fundo) × móvel (não divide), como no Promob
  - Origem no legado: `types_closets.py:635-689`, `:1194-1242`
  - Critério de pronto: prateleira fixa divide a abertura e o fundo; móvel não
  - Confiança: 🟢 (A2) / 🟡 (fundo dividido, Q-07)

- [ ] T-10, Recuos frontal/traseiro configuráveis em divisórias e prateleiras
  - Origem no legado: ausente; Promob `10-projeto-ii.md#10-10-1-tipos-de-divisoes`
  - Critério de pronto: recuo do preset aplicado às peças internas
  - Confiança: 🟡 (Q-10)

### Bloco C — Inserções

- [ ] T-11, Regeneradores (`_reconcile_*`) idempotentes
  - Origem no legado: `types_closets.py:1011-1242`
  - Critério de pronto: rodar 2× não cria nem apaga peças
  - Confiança: 🟢

- [ ] T-12, Portas (simples, dupla, basculante, do vão) com meia sobreposição, estilos e vidro
  - Origem no legado: `types_closets.py:716-797`, `:1036-1127`; `fronts_closets.py`; `materials_closets.py:411-464`
  - Critério de pronto: RN-16, RN-17, RN-22, RN-23
  - Confiança: 🟢

- [ ] T-13, Gavetas: pilha que preenche, tampa por prateleira fixa, caixa por sistema
  - Origem no legado: `types_closets.py:810-878`, `:1813-1831`; `drawer_boxes_closets.py:40-85`; `ops_closet.py:1949-1974`
  - Critério de pronto: RN-18..RN-21
  - Confiança: 🟢

- [ ] T-14, Catálogo de caixas/corrediças como dados (Metabox, Avantech, madeira, corrediça telescópica comum)
  - Origem no legado: `drawer_boxes_closets.py:30-85`
  - Critério de pronto: adicionar um sistema não exige editar Python
  - Confiança: 🟡 (Q-06)

- [ ] T-15, Varões e cabides; reguláveis; nichos
  - Origem no legado: `types_closets.py:736-778`, `:880-904`, `:1154-1183`; `pulls_closets.py:176-240`
  - Critério de pronto: RN-25..RN-27
  - Confiança: 🟢

- [ ] T-16, Presets de vão e de abertura (`apply_bay_config`, `apply_opening_config`); `DOORS_OPEN_*` abrindo portas conforme o comentário ou o nome corrigido; remover `_cfg_hamper`
  - Origem no legado: `types_closets.py:2065-2260`
  - Critério de pronto: RN-28; cada preset coberto por teste
  - Confiança: 🟢

- [ ] T-17, Frentes, puxadores e portas do lado BACK da ilha dupla
  - Origem no legado: `types_closets.py:914-915`, `:1037-1039`
  - Critério de pronto: ilha dupla com frentes e puxadores nos dois lados
  - Confiança: 🔴 (Q-05)

### Bloco D — Inserção e tipos especiais

- [ ] T-18, `place_starter` com `invoke`, auto nº de vãos (vão máx. do preset), recuo de canto, ilhas com detentes e `try/except` que limpa o handler de cotas
  - Origem no legado: `ops_closet.py:26-27`, `:399-1483`
  - Critério de pronto: cenários de inserção; exceção no modal não deixa handler órfão
  - Confiança: 🟢

- [ ] T-19, Vizinho de canto e folga de canto com pontes
  - Origem no legado: `ops_closet.py:170-288`, `:2513-2653`; `types_closets.py:1279-1339`
  - Critério de pronto: RN-31
  - Confiança: 🟢

- [ ] T-20, Ilha dupla e L-shelf
  - Origem no legado: `types_closets.py:1471-1720`
  - Critério de pronto: RN-32; remover expressões mortas de `LShelfClosetStarter.recalculate` (`:1675, 1678`)
  - Confiança: 🟢

### Bloco E — Edição

- [ ] T-21, Overlay GPU de rótulos editáveis com unidade do usuário
  - Origem no legado: `gpu_overlay_closets.py:160-720`
  - Critério de pronto: `parse_distance` aceita `mm`/`cm`/`m` e vírgula (decisão PL-03)
  - Confiança: 🟢

- [ ] T-22, Grab com snap 32 mm e snapshot/rollback, desenhando com `POLYLINE_UNIFORM_COLOR`
  - Origem no legado: `op_grab_closet.py:41-845`
  - Critério de pronto: RN-10, RN-35; linhas grossas visíveis em Vulkan/Metal
  - Confiança: 🟢

- [ ] T-23, Estrutura: inserir/excluir vão, copiar/colar vão e abertura, remover peça por config, duplicar espelhado
  - Origem no legado: `types_closets.py:1344-1443`, `:1958-2005`; `ops_closet.py:360-386`, `:1491-2390`
  - Critério de pronto: RN-33, RN-34, RN-36
  - Confiança: 🟢

- [ ] T-24, Operadores com `bl_idname` `btm.*` e `UNDO` (incluindo `toggle_mode` e `open_door_mode`); sem `bpy.ops` em callback `update=`
  - Origem no legado: `ops_closet.py:294-354`; `op_open_door_closet.py:82`; `props_closets.py:97-100`
  - Critério de pronto: Ctrl+Z desfaz troca de modo e abertura de porta
  - Confiança: 🟢

### Bloco F — Opções de sala e acabamentos

- [ ] T-25, Opções de sala (materiais, frentes, puxadores, varões, cabides, caixas) agrupadas num único recálculo por starter
  - Origem no legado: `materials_closets.py:307`, `fronts_closets.py:230`, `pulls_closets.py:384`, `drawer_boxes_closets.py:107`
  - Critério de pronto: trocar a opção de sala → 1 recálculo por starter
  - Confiança: 🟢

- [ ] T-26, Materiais sem `use_nodes`; objetos gerados na coleção do produto
  - Origem no legado: `materials_closets.py:121`; `types_closets.py:1001`; `pulls_closets.py:221`; `molding_closets.py:482, 523`
  - Critério de pronto: `check_api.py` limpo; nenhum objeto do closet solto em `scene.collection`
  - Confiança: 🟢

- [ ] T-27, `user_hangers_dir` via `extension_path_user(__package__, …)` sem montar o pacote à mão
  - Origem no legado: `pulls_closets.py:61-72`
  - Critério de pronto: funciona instalado como extensão e em desenvolvimento
  - Confiança: 🟢

- [ ] T-28, Moldura de coroa e tampo, com moldura marcada como desatualizada quando o starter muda
  - Origem no legado: `molding_closets.py:26-218`, `:393-405`; `types_closets.py:1244-1269`
  - Critério de pronto: RN-37, RN-38; aviso de moldura desatualizada
  - Confiança: 🟡 (Q-09)

- [ ] T-29, Abrir/fechar portas e gavetas com tween, sem recálculo
  - Origem no legado: `op_open_door_closet.py:34-185`; `types_closets.py:1770-1864`
  - Critério de pronto: 0,35 s; estado persistido; undo funciona
  - Confiança: 🟢

### Bloco G — Produção

- [ ] T-30, Lista de corte das peças do closet (painéis, prateleiras, fundos, frentes, caixas) com fita de borda e veio
  - Origem no legado: ausente; veio em `props_closets.py:281-294`, `materials_closets.py:139-150`
  - Critério de pronto: starter gera lista de corte completa no `cutting/`
  - Confiança: 🔴 (Q-03)

- [ ] T-31, Furação 32 mm (linha de furos para pinos, minifix, dobradiças, corrediças) por peça
  - Origem no legado: ausente; retícula em `const_closets.py:126-140`
  - Critério de pronto: cada painel lista os furos com posição, diâmetro e profundidade
  - Confiança: 🔴 (Q-02)

## Tarefas de Teste

- [ ] TT-01, Solver puro: iguais, travados, todos travados, mínimo violado
- [ ] TT-02, Sistema 32 mm: alturas de painel e encaixe de furos
- [ ] TT-03, Gavetas: Metabox/Avantech/madeira, nada cabe, pilha que preenche
- [ ] TT-04, Presets de vão e de abertura (15 + 12) sem exceção
- [ ] TT-05, Regeneradores idempotentes
- [ ] TT-06, Inserção: auto vãos, canto interno, ilha com detentes, vizinho de canto
- [ ] TT-07, Grab: snap 32 mm, rollback, carregar arquivo com grab ativo
- [ ] TT-08, Ilha dupla com frentes no BACK (T-17)
- [ ] TT-09, `register()`/`unregister()` 2× com grab e open door ativos
- [ ] TT-10, Lista de corte e furação de um starter (T-30, T-31)

## Tarefas de Migração de Dados

- [ ] TM-01, Preservar idprops de configuração (`hb_*`) e tags (`IS_CLOSET_*`) dos arquivos existentes
  - Confiança: 🟢
- [ ] TM-02, Gravar `closet_type` correto em ilhas duplas e L-shelves existentes (T-04)
  - Confiança: 🟡
- [ ] TM-03, Não converter starters existentes ao trocar o preset de medidas
  - Confiança: 🟡

## Ordem Sugerida
1. **Bloco B** (solver puro e recálculo) e **A** (dados) primeiro.
2. **Bloco C** (inserções), depois **D** (inserção e especiais) e **E** (edição).
3. **Bloco F** em paralelo com E.
4. **Bloco G** (produção) assim que B e C estabilizarem — o closet é a unit legada mais próxima da fabricação brasileira
   (sistema 32 mm).
5. Bloqueios: T-01 ← Q-01; T-31 ← Q-02; T-30 ← Q-03; T-08 ← Q-04; T-17 ← Q-05; T-14 ← Q-06; T-09 ← Q-07; T-04 ← Q-08;
   T-28 ← Q-09; T-10 ← Q-10.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 2 (2026-10-01) — ver **Decisões da rodada 2** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Medidas brasileiras do roupeiro.
- Q-02 Furação 32 mm.
- Q-03 Lista de corte.
- Q-04 Fundo e cleat.
- Q-05 Frentes do lado BACK da ilha dupla.
- Q-06 Catálogo de caixas e corrediças.
- Q-07 Prateleira fixa dividindo o fundo.
- Q-08 Tipos de starter para ilha dupla e L-shelf.
- Q-09 Moldura desatualizada × regeneração automática.
- Q-10 Recuos de divisórias e prateleiras.

## Decisões da rodada 2 (2026-10-01)

Todas as recomendações ⭐ foram aceitas. As tarefas listadas saem do estado bloqueado e seguem a decisão.

| Pergunta | Decisão | Tarefas desbloqueadas |
|---|---|---|
| Q-01 | Chapa 15 ou 18 mm; profundidade 550–600 mm (com cabide frontal 300–350 mm); vão máximo 800–900 mm para prateleira; alturas pelo sistema 32 mm; puxador ~1000–1100 mm do piso; frente de gaveta conforme a corrediça. | T-01 |
| Q-02 | Sim, na fase de produção, como dados por peça para CNC/etiqueta. | T-31 |
| Q-03 | Sim. | T-30 |
| Q-04 | Preset BR: fundo 6 mm encaixado em rasgo com recuo; cleat opcional (fixação por suporte/cantoneira). | T-08 |
| Q-05 | Sim. | T-17 |
| Q-06 | Sim. | T-14 |
| Q-07 | Sim. | T-09 |
| Q-08 | Sim. | T-04 |
| Q-09 | Marcar desatualizada com "Refazer" (igual a bancada/molduras do frameless, Q-05 de lá). | T-28 |
| Q-10 | Sim, valores no preset. | T-10 |
