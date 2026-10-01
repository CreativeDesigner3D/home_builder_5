# frameless — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-30, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Caminhos relativos a `blendertomob/product_libraries/frameless/` salvo indicação.

## Pré-requisitos
- [ ] [`hb_core`](../hb_core/tasks.md) blocos A–C prontos (ponte GN por nome em `compat.py`, `GeoNodeObject`, prompts,
      calculadora com clamp em 0 — decisão Q-09 de `hb_core`).
- [ ] [`hb_placement`](../hb_placement/tasks.md) pronto (mixin de inserção, vão livre mais próximo, alternador
      "Evitar Sobreposição").
- [ ] [`product_common`](../product_common/tasks.md) blocos A e D (motor de porta, eletrodomésticos).
- [ ] **Preset de medidas** BR (padrão) / EUA alternável definido (`product_common` Q-06, `hb_core` T-27): todos os
      padrões desta unit passam a vir do preset ativo, não de constantes em polegadas.
- [ ] Interfaces de `CPM_CORNERNOTCH`, `CPM_CHAMFER`, `CPM_CUTOUT`, `CPM_5PIECEDOOR` conferidas em
      [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md).
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`.

## Tarefas

### Bloco A — Propriedades, registro e preset

- [ ] T-01, `Frameless_Scene_Props` com leitura por atributo, `# type: ignore` e padrões vindos do preset (BR: chapa
      15/18 mm, inferior/aéreo/alto em mm)
  - Origem no legado: `props_hb_frameless.py:1341-2518`
  - Critério de pronto: trocar o preset atualiza os padrões; nenhum valor default nasce de `units.inch()` fora do preset EUA
  - Confiança: 🟢 (estrutura) / 🟡 (valores BR, Q-04)

- [ ] T-02, `register()`/`unregister()` sem engolir exceções; desfaz `Scene.hb_frameless` e `Scene.hb_template_*`
  - Origem no legado: `__init__.py:10-14`, `props_hb_frameless.py:2537-2558`, `operators/ops_placement.py:1986-2007`
  - Critério de pronto: registrar/desregistrar 2× seguidas sem resíduo nem erro silencioso
  - Confiança: 🟢

- [ ] T-03, Callbacks `update=` sem `bpy.ops` (modo de seleção chama função direta) e alturas derivadas do pé-direito
  - Origem no legado: `props_hb_frameless.py:426-456`
  - Critério de pronto: mudar `frameless_selection_mode` não chama operador; RN-30 verificada
  - Confiança: 🟢

- [ ] T-04, Enums dinâmicos (puxadores, cores) com cache das strings e sem I/O a cada redraw
  - Origem no legado: `props_hb_frameless.py:108-134`, `finish_colors.py:207-225`
  - Critério de pronto: enum estável após 100 redraws; arquivo JSON lido só quando muda
  - Confiança: 🟢

- [ ] T-05, Unificar a origem dos padrões: sempre `hb_project.get_main_scene().hb_frameless`
  - Origem no legado: 77 leituras de `bpy.context.scene.hb_frameless` × 89 da cena principal
  - Critério de pronto: criar gabinete numa cena de layout usa os mesmos padrões da cena principal
  - Confiança: 🟡 (Q-09)

### Bloco B — Carcaças

- [ ] T-06, `Cabinet.create_cabinet` e prompts do gabinete
  - Origem no legado: `types_frameless.py:8-50`, `:114`
  - Critério de pronto: prompts de RN-01..RN-07 criados como ID properties
  - Confiança: 🟢

- [ ] T-07, `create_base_carcass` com rodapé 0/2/3, topo inteiro/travessas/avental e "Remove Bottom"
  - Origem no legado: `types_frameless.py:125-313`
  - Critério de pronto: cenários "Inferior padrão" e "Remove Bottom" de `requirements.md`
  - Confiança: 🟢

- [ ] T-08, `create_tall_carcass` e `create_upper_carcass`
  - Origem no legado: `types_frameless.py:315-535`
  - Critério de pronto: vão do aéreo `dim_z − 2mt`; alto desconta `mt` do tampo
  - Confiança: 🟢

- [ ] T-09, Fundo configurável: chapa cheia (legado) ou fundo fino encaixado/parafusado
  - Origem no legado: `types_frameless.py:206-216`, `:401`
  - Critério de pronto: modo escolhido muda profundidade do vão e gera a peça de fundo com espessura própria
  - Confiança: 🔴 (Q-04)

- [ ] T-10, Reconstruir a carcaça ao trocar `Toe Kick Type` depois da criação
  - Origem no legado: `types_frameless.py:144`, `ops_defaults.py:19-26`
  - Critério de pronto: trocar 0 → 3 cria niveladores e remove o entalhe
  - Confiança: 🟡 (Q-10)

- [ ] T-11, Niveladores (`_add_leg_levelers`) carregando o asset uma vez por sessão
  - Origem no legado: `types_frameless.py:77-92`
  - Critério de pronto: 4 niveladores com inset `lli`; sem datablocks duplicados
  - Confiança: 🟢

### Bloco C — Vãos e splitters

- [ ] T-12, `add_cage_to_bay` e Bay com origem/dimensões de RN-06
  - Origem no legado: `types_frameless.py:52`, `:292-300`, `:527-535`
  - Critério de pronto: Bay acompanha `Dim X/Y/Z` do gabinete
  - Confiança: 🟢

- [ ] T-13, `SplitterVertical`/`SplitterHorizontal` com calculadora, checando o tamanho de `opening_sizes`
  - Origem no legado: `types_frameless.py:918-1140`
  - Critério de pronto: cenário "Rateio com um vão fixo"; lista curta → completa com 0 (igual), sem `IndexError`
  - Confiança: 🟢

- [ ] T-14, Recalcular a calculadora quando `Dim Z` do splitter muda
  - Origem no legado: `types_frameless.py:963`; `hb_props.py:294-330`
  - Critério de pronto: redimensionar o gabinete redistribui os vãos iguais sem ação manual
  - Confiança: 🟡 (Q-06)

- [ ] T-15, `change_bay_opening` com os 30 tipos e realocação de puxadores
  - Origem no legado: `operators/ops_opening.py:22-213`, `:587`
  - Critério de pronto: cada tipo cria a configuração de RN-21; puxadores seguem RN-23/RN-24
  - Confiança: 🟢

- [ ] T-16, Splitters customizados (vertical/horizontal) e de interior
  - Origem no legado: `operators/ops_opening.py:1097-…`, `operators/ops_interior.py:271-826`, `types_frameless.py:2050-2277`
  - Critério de pronto: divisões criadas pelo diálogo com a mesma regra de rateio
  - Confiança: 🟢

### Bloco D — Frentes, sobreposição e puxadores

- [ ] T-17, Prompts de abertura e empty "Overlay Prompt Obj" (inset/meia/total)
  - Origem no legado: `types_frameless.py:1156-1210`
  - Critério de pronto: cenário "Sobreposição total"; sem ciclo de dependência no depsgraph
  - Confiança: 🟢

- [ ] T-18, Ligar `Left/Right/Top/Bottom Thickness` ao `Material Thickness` do gabinete por driver
  - Origem no legado: `types_frameless.py:1156-1169`; `ops_defaults.py:31-56`
  - Critério de pronto: mudar a espessura do gabinete corrige os overlays sem rodar `update_material_thickness_prompts`
  - Confiança: 🟢

- [ ] T-19, Portas (simples/dupla, Door Swing), gavetas, basculantes, pullouts e frentes falsas
  - Origem no legado: `types_frameless.py:1271-1443`, `:1734-1926`
  - Critério de pronto: RN-16; frente falsa sem caixa e sem puxador
  - Confiança: 🟢

- [ ] T-20, Sobreposição BR: valores de reveal/gaps do preset (ex.: total = espessura − 1,5 a 2 mm)
  - Origem no legado: `types_frameless.py:1156-1176`
  - Critério de pronto: preset BR gera overlay coerente com lateral de 15/18 mm
  - Confiança: 🟡 (Q-04)

- [ ] T-21, Puxadores por `Pull Location`, posições da cena e comprimento do objeto
  - Origem no legado: `types_frameless.py:1747-1862`; `props_hb_frameless.py:37-353`, `:1625-1652`
  - Critério de pronto: RN-22; sem objeto → comprimento 0,1016 m
  - Confiança: 🟢

### Bloco E — Interiores e gavetas

- [ ] T-22, Prateleiras reguláveis em array com quantidade padrão
  - Origem no legado: `types_frameless.py:1222-1264`, `:1330-1342`; `operators/ops_interior.py:7-37`
  - Critério de pronto: RN-17/RN-18
  - Confiança: 🟢

- [ ] T-23, Caixas de gaveta com folgas do preset e inclusão/remoção global
  - Origem no legado: `types_frameless.py:1867-1926`; `props_hb_frameless.py:436-450`
  - Critério de pronto: RN-19/RN-20; folgas laterais compatíveis com corrediças nacionais (12,5–13 mm)
  - Confiança: 🟢

### Bloco F — Tipos especiais e cantos

- [ ] T-24, Lap Drawer, gabinete de geladeira, alto e aéreo empilhados
  - Origem no legado: `types_frameless.py:623-902`
  - Critério de pronto: RN-08, RN-09, RN-11
  - Confiança: 🟢

- [ ] T-25, Cantos pie-cut (inferior, alto, aéreo) com portas articuladas
  - Origem no legado: `types_frameless.py:2280-2446`
  - Critério de pronto: RN-12; inserção encosta na ponta da parede
  - Confiança: 🟢

- [ ] T-26, Cantos diagonais completos (ou remoção da UI)
  - Origem no legado: `types_frameless.py:2318-2324`, `:2747`
  - Critério de pronto: decisão aplicada
  - Confiança: 🔴 (Q-01)

- [ ] T-27, Rodapé Ladder, rollouts e TRAY_DIVIDERS (ou remoção)
  - Origem no legado: `types_frameless.py:2160-2162`, `:2275-2277`
  - Critério de pronto: decisão aplicada
  - Confiança: 🔴 (Q-02)

### Bloco G — Inserção

- [ ] T-28, `place_cabinet` sobre o mixin de `hb_placement`, com `invoke` explícito
  - Origem no legado: `operators/ops_placement.py:270-1863`
  - Critério de pronto: cenários de inserção de `requirements.md`; `EXEC_DEFAULT` não entra em modal
  - Confiança: 🟢

- [ ] T-29, Preview com `HB_CURRENT_DRAW_OBJ` (decisão `hb_placement` Q-05 → T-25)
  - Origem no legado: `operators/ops_placement.py:576`
  - Critério de pronto: o raycast nunca acerta o próprio preview
  - Confiança: 🟢

- [ ] T-30, Constantes de inserção do preset (largura máx. de preenchimento, snap de centro, parede mais próxima, Z do aéreo)
  - Origem no legado: `operators/ops_placement.py:464-505`, `:1057-1085`, `:1182-1262`, `:1690`
  - Critério de pronto: preset BR usa valores em mm; EUA reproduz 36"/4"/6"/54"
  - Confiança: 🟡 (Q-04)

- [ ] T-31, `toggle_mode` e `draw_cabinet` com `UNDO` onde alteram dados
  - Origem no legado: `operators/ops_placement.py:1866-1932`
  - Critério de pronto: Ctrl+Z desfaz a troca de modo
  - Confiança: 🟢

### Bloco H — Estilos e materiais

- [ ] T-32, Estilo de gabinete: materiais por face, fita, CPM, overlay respeitando `FORCE_HALF_OVERLAY_*`
  - Origem no legado: `props_hb_frameless.py:693-866`
  - Critério de pronto: RN-26/RN-27; meia sobreposição entre vãos preservada
  - Confiança: 🟢

- [ ] T-33, Vincular estilo por identificador estável (não por índice)
  - Origem no legado: `operators/ops_styles.py:376-422`
  - Critério de pronto: remover/reordenar estilos não troca o estilo de nenhum gabinete
  - Confiança: 🟢

- [ ] T-34, Estilo de porta com mínimo unificado +1" (constante de `product_common`) e mensagem ao usuário
  - Origem no legado: `props_hb_frameless.py:1044-1162`
  - Critério de pronto: frente pequena gera `report` visível, não só string de retorno
  - Confiança: 🟢

- [ ] T-35, Materiais sem `use_nodes`/`blend_method` obsoletos; catálogo de acabamentos do preset (BR: padrões de MDF BP)
  - Origem no legado: `props_hb_frameless.py:269, 310, 313`; `wood_materials.py`; `finish_colors.py`
  - Critério de pronto: `check_api.py` limpo; preset BR lista acabamentos nacionais
  - Confiança: 🟢 (API) / 🟡 (catálogo BR, Q-04)

- [ ] T-36, Pintura em lote por timer sem guardar referências a IDs entre ticks
  - Origem no legado: `operators/ops_styles.py:673-789`
  - Critério de pronto: undo durante o lote não causa erro
  - Confiança: 🟡

### Bloco I — Pós-processamento

- [ ] T-37, Bancada por corrida, grupo e ilha, com recorte booleano
  - Origem no legado: `operators/ops_countertop.py:6-752`
  - Critério de pronto: cenários de bancada de `requirements.md`
  - Confiança: 🟢

- [ ] T-38, Crown, rodapé decorativo e moldura inferior com código de agrupamento único
  - Origem no legado: `operators/ops_crown.py`, `ops_toe_kick.py`, `ops_upper_bottom.py`
  - Critério de pronto: um módulo comum de adjacência/offset; os três operadores o usam
  - Confiança: 🟢

- [ ] T-39, Atualização automática de bancada/molduras quando o gabinete muda
  - Origem no legado: geometria estática (`ops_countertop.py`, `ops_crown.py`)
  - Critério de pronto: redimensionar um gabinete atualiza (ou marca como desatualizada) a bancada
  - Confiança: 🔴 (Q-05)

- [ ] T-40, Laterais aplicadas ligadas aos prompts (sem `0,875"` embutido na expressão)
  - Origem no legado: `operators/ops_cabinet.py:175-335`, `operators/ops_finished_ends.py:58-396`
  - Critério de pronto: mudar a espessura da frente atualiza a profundidade da lateral
  - Confiança: 🟢

### Bloco J — Produtos

- [ ] T-41, Prateleira flutuante, sanca, Support Frame, meia-parede, pernas, painel e peça avulsa
  - Origem no legado: `types_products.py:8-905`, `operators/ops_products.py`
  - Critério de pronto: RN-38..RN-41; meia-parede com nomes corretos de peças ("Top"/"Bottom", não "Right End")
  - Confiança: 🟢

### Bloco K — Templates, biblioteca, snap e limpeza

- [ ] T-42, Templates Geladeira/Fogão e Ilha com preview (ou templates brasileiros)
  - Origem no legado: `props_elevation_templates.py:18-1576`
  - Critério de pronto: preview e geração conforme RN-42/RN-43
  - Confiança: 🟡 (Q-07)

- [ ] T-43, Biblioteca do usuário com miniatura que restaura as configurações de render da cena
  - Origem no legado: `operators/ops_library.py:99-307`
  - Critério de pronto: depois de salvar, `film_transparent`/`use_freestyle`/`line_thickness` voltam ao valor anterior
  - Confiança: 🟢

- [ ] T-44, Linhas de snap reutilizando um único material
  - Origem no legado: `operators/ops_snap_line.py:7-61`
  - Critério de pronto: 10 linhas → 1 material
  - Confiança: 🟢

- [ ] T-45, Limpeza de malha (BMesh) com `UNDO`
  - Origem no legado: `operators/ops_cleanup.py`
  - Critério de pronto: Ctrl+Z restaura a malha
  - Confiança: 🟢

- [ ] T-46, Remover ou implementar propriedades sem efeito
  - Origem no legado: `props_hb_frameless.py:1391-1555`, `:997`, `:922-931`; `props_elevation_templates.py:309-319`
  - Critério de pronto: nenhuma propriedade na UI sem efeito
  - Confiança: 🔴 (Q-03)

### Bloco L — Produção

- [ ] T-47, Expor as `CabinetPart` do frameless ao `cutting/part_extractor.py` (dimensões, espessura, fita, veio)
  - Origem no legado: ausente (lacuna L1 de `soul.md`); peças com `Finish Top/Bottom` e fita em `props_hb_frameless.py:700-736`
  - Critério de pronto: gabinete inferior gera lista de corte com todas as peças e bordas
  - Confiança: 🔴 (Q-08)

## Tarefas de Teste

- [ ] TT-01, Carcaça do inferior (rodapé 0/2/3, Remove Bottom, topo 0/1/2) em `--background`
- [ ] TT-02, Splitter: rateio, lista curta, redimensionamento (T-14)
- [ ] TT-03, Overlay inset/meia/total e porta dupla; sem ciclo no depsgraph
- [ ] TT-04, Caixa de gaveta e prateleiras padrão por profundidade/altura
- [ ] TT-05, `change_bay_opening` para os 30 tipos sem exceção
- [ ] TT-06, Inserção: preenchimento automático, piso, canto na ponta (com eventos simulados)
- [ ] TT-07, Estilos: remover/reordenar não troca estilos de gabinetes (T-33); porta pequena reporta erro
- [ ] TT-08, Bancada com fogão no meio e ponta junto a alto
- [ ] TT-09, Preset BR × EUA: mesmas classes geram medidas diferentes coerentes
- [ ] TT-10, `register()`/`unregister()` 2× sem resíduo
- [ ] TT-11, Lista de corte do frameless (T-47) bate com as peças visíveis

## Tarefas de Migração de Dados

- [ ] TM-01, Converter `CABINET_STYLE_INDEX`/`DOOR_STYLE_INDEX` para o identificador estável de T-33 ao abrir arquivos antigos
  - Origem: `operators/ops_styles.py:376-422`
  - Confiança: 🟢
- [ ] TM-02, Preservar prompts e marcadores (`IS_FRAMELESS_*`, `FORCE_HALF_OVERLAY_*`, `Finish Top/Bottom`) como ID properties
  - Confiança: 🟢
- [ ] TM-03, Arquivos antigos mantêm medidas em polegadas: não converter gabinetes existentes ao trocar o preset
  - Confiança: 🟡

## Ordem Sugerida
1. **Bloco A** (preset e props) e **B** (carcaças): base de tudo.
2. **Blocos C, D e E** em sequência: vão → frentes → interiores.
3. **Bloco G** (inserção) assim que B–D estiverem prontos; **H** (estilos) em paralelo.
4. **Blocos F, I, J, K** depois; **L** (produção) assim que B e D estabilizarem, pois é o objetivo do produto.
5. Bloqueios: T-09/T-20/T-30/T-35 ← Q-04; T-14 ← Q-06; T-10 ← Q-10; T-26 ← Q-01; T-27 ← Q-02; T-39 ← Q-05;
   T-42 ← Q-07; T-46 ← Q-03; T-47 ← Q-08; T-05 ← Q-09.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 2 (2026-10-01) — ver **Decisões da rodada 2** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Cantos diagonais: completar ou remover.
- Q-02 Rodapé Ladder, rollouts e TRAY_DIVIDERS.
- Q-03 Propriedades de cena sem efeito.
- Q-04 Construção brasileira: fundo, espessuras, sobreposição, acabamentos.
- Q-05 Bancada e molduras estáticas × paramétricas.
- Q-06 Calculadora do splitter como recálculo automático.
- Q-07 Templates de elevação para o mercado brasileiro.
- Q-08 Integração com a lista de corte.
- Q-09 Cena corrente × cena principal como fonte dos padrões.
- Q-10 Reconstruir ao trocar o tipo de rodapé.

## Decisões da rodada 2 (2026-10-01)

Todas as recomendações ⭐ foram aceitas. As tarefas listadas saem do estado bloqueado e seguem a decisão.

| Pergunta | Decisão | Tarefas desbloqueadas |
|---|---|---|
| Q-01 | Retirar até haver demanda; manter pie-cut (L). | T-26 |
| Q-02 | Remover Ladder e TRAY_DIVIDERS; rollouts como acessório (`product_common` registries). | T-27 |
| Q-03 | Remover todas, exceto `show_machining`, que fica reservada para a furação (produção). | T-46 |
| Q-04 | Laterais passantes; chapa 15 ou 18 mm (escolha por peça); fundo 6 mm encaixado em rasgo (ou parafusado) com recuo configurável; rodapé ~100 mm com recuo ~50 mm; inferior 850–900 mm com tampo, prof. 550–600 mm; aéreo prof. 300–350 mm; sobreposição total = espessura − 1,5 a 2 mm; acabamentos de MDF BP. | T-01, T-09, T-20, T-30, T-35 |
| Q-05 | Continuar estáticos, mas **marcados como desatualizados** quando um gabinete do grupo muda, com "Refazer" em 1 clique. | T-39 |
| Q-06 | Sim. | T-14 |
| Q-07 | Manter os dois com medidas BR e adicionar "Cozinha linear com pia" e "Área de serviço". | T-42 |
| Q-08 | Sim — é o objetivo do produto. | T-47 |
| Q-09 | Sim. | T-05 |
| Q-10 | Sim, reconstruir preservando estilo, vãos e frentes. | T-10 |
