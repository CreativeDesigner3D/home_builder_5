# hb_core — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Pré-requisitos
- [ ] Node groups `geometry_nodes/*.blend` e `geometry_nodes/CabinetPartModifiers/*.blend` disponíveis, com as
      interfaces (nomes de inputs) documentadas — hoje é 🔴 (ver `questions.md`, Q-01).
- [ ] `compat.py` como único ponto de diferença de versão (regra do `CLAUDE.md`).
- [ ] `data/units.py` disponível (a fachada `units.py` só reexporta).
- [ ] Assinaturas de API confirmadas no RAG (`python3 docs/rag/tools/rag_search.py --symbol …`) e
      `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`.

## Tarefas

### Bloco A — Ponte de versão e cache de sockets

- [ ] T-01, Consolidar a ponte de inputs GN em `compat.py` com API por **nome** e por **identificador**
  - Origem no legado: `hb_utils.py:13-60`, `compat.py:9-88`, `hb_types.py:21-57`
  - Critério de pronto: `hb_utils.get_gn_input/set_gn_input/gn_input_data_path` passam a delegar a `compat`; um único
    `_INPUT_IDENT_CACHE`; testes de leitura/escrita em 5.2 passam
  - Confiança: 🟢

- [ ] T-02, Trocar a chave do cache de `id(node_group)` por uma chave estável (ex.: `node_group.name_full` +
      `session_uid`, ou invalidação por handler `depsgraph_update_post`)
  - Origem no legado: `hb_types.py:24-50`
  - Critério de pronto: após apagar e recriar um node group homônimo, `set_input` escreve no socket certo sem depender do retry
  - Confiança: 🟡

- [ ] T-03, Implementar `set_input`/`get_input` com validação em 4 etapas, `ValueError` explícito, retry único e `update_tag()`
  - Origem no legado: `hb_types.py:325-390`, `:914-962`
  - Critério de pronto: cenários "Escrever input inexistente" e "Cache desatualizado" de `requirements.md` passam
  - Confiança: 🟢

### Bloco B — Modelo de objetos

- [ ] T-04, `GeoNodeObject.create` e `create_curve` com carga do node group por append apenas se ausente
  - Origem no legado: `hb_types.py:79-122`
  - Critério de pronto: criar 2 objetos não duplica o grupo; `mod_name` preenchido; curva POLY com 2 pontos e cor de anotação
  - Confiança: 🟢

- [ ] T-05, DSL de drivers: `Variable`, `var_*`, `driver_*`, `add_driver_variables`
  - Origem no legado: `hb_types.py:59-68,167-287`, `hb_utils.py:299-305`
  - Critério de pronto: driver `Dim X = largura − 2·mt` atualiza após mudar a largura; eixo inválido gera `ValueError`
    (corrige o `UnboundLocalError` legado)
  - Confiança: 🟢

- [ ] T-06, Registrar `IF/OR/AND` em `driver_namespace` somente com os três nomes (sem dunders) e removê-los em `unregister()`
  - Origem no legado: `hb_driver_functions.py:1-26`, `__init__.py:58-73,249-256`
  - Critério de pronto: após `unregister()`, `"IF" not in bpy.app.driver_namespace`; após `load_post`, disponíveis de novo
  - Confiança: 🟢

- [ ] T-07, Subclasses: `GeoNodeCage`, `GeoNodeRectangle`, `GeoNodeCutpart`, `GeoNode5PieceDoor`, `GeoNodeHardware`,
      `GeoNodeDrawerBox`, `GeoNodeDoorSwing`, `GeoNodeArrow` com marcadores e padrões de fábrica
  - Origem no legado: `hb_types.py:563-629,801-840`
  - Critério de pronto: cada subclasse cria o objeto com os padrões de RN-07/RN-08
  - Confiança: 🟢

- [ ] T-08, `CabinetPartModifier` (`CPM_*`) com carga opcional do node group
  - Origem no legado: `hb_types.py:843-962`
  - Critério de pronto: token inexistente não quebra; `driver_hide` controla `show_viewport/show_render` com expressão invertida documentada
  - Confiança: 🟢

### Bloco C — Propriedades, calculadora e reavaliação

- [ ] T-09, PropertyGroups `Object/Scene/WindowManager.home_builder` com `# type: ignore` e leitura por atributo
  - Origem no legado: `hb_props.py:227-822`
  - Critério de pronto: `unregister()` remove os 3 ponteiros; `register()` **não** engole exceções (loga e relança)
  - Confiança: 🟢

- [ ] T-10, `add_property` com os 6 tipos; tratar `COMBOBOX` via `id_properties_ensure()` + `id_properties_ui().update(...)`
      e adicionar o tipo `TEXT` (usado por "Hood Style"/"Sink Type" em `product_common`)
  - Origem no legado: `hb_props.py:335-374`, `types_appliances.py:176,192`
  - Critério de pronto: cada tipo cria a ID prop com subtype/min/max corretos no 5.2; `TEXT` cria string
  - Confiança: 🟡

- [ ] T-11, `Calculator.calculate` com a regra de distribuição (RN-10) e **aviso** quando o resultado for negativo
  - Origem no legado: `hb_props.py:249-320`
  - Critério de pronto: cenários de calculadora passam; resultado < 0 gera aviso (sem mudar o valor, para paridade)
  - Confiança: 🟢

- [ ] T-12, `run_calc_fix` / `run_calc_fix_until_stable` com comparação por nome de objeto (não por `zip`)
  - Origem no legado: `hb_utils.py:190-297`
  - Critério de pronto: retorna nº de passadas ou −1; criar/apagar objetos entre passadas não desalinha a comparação
  - Confiança: 🟢

- [ ] T-13, Callbacks de update da cena: pé-direito, material de parede, anotações, molduras, gaiolas de porta/janela
  - Origem no legado: `hb_props.py:29-225`
  - Critério de pronto: RF-14 e RF-15 passam; `annotation_dimension_extend_line` usa um callback próprio que reescreve `Extend Line`
  - Confiança: 🟢

### Bloco D — Paredes, cotas e hierarquia

- [ ] T-14, `GeoNodeWall` com `obj_x`, `connect_to_wall` e `get_connected_wall(direction, include_loop_seam)`
  - Origem no legado: `hb_types.py:431-561`
  - Critério de pronto: cenários de paredes passam; percorrer uma cadeia fechada com `include_loop_seam=False` termina
  - Confiança: 🟢

- [ ] T-15, Remover ou reescrever `GeoNodeWall.assign_materials` usando os mesmos inputs de `update_wall_material`
  - Origem no legado: `hb_types.py:468-478`, `hb_props.py:211-225`
  - Critério de pronto: um único caminho de atribuição de material de parede
  - Confiança: 🔴 (depende de Q-04)

- [ ] T-16, `GeoNodeDimension`: `get_unit_type`, `create`, `set_decimal(fine)` e fixup `ensure_dimension_text_offset_basis`
  - Origem no legado: `hb_types.py:632-798`
  - Critério de pronto: RF-11..RF-13; cota em cena `MM` mostra `Unit Type = 2`
  - Confiança: 🟢

- [ ] T-17, `get_*_bp` (subida por marcadores) e `delete_obj_and_children`
  - Origem no legado: `hb_utils.py:67-187`
  - Critério de pronto: RF-19 e RF-20
  - Confiança: 🟢

### Bloco E — Projeto, obstáculos e unidades

- [ ] T-18, `hb_project`: cena principal única, migração, cenas de cômodo; unificar as duas definições de `is_room_scene`
  - Origem no legado: `hb_project.py:30-289`, `hb_utils.py:461-469`
  - Critério de pronto: RF-16/RF-17; uma só `is_room_scene` (excluindo layout, detalhe e crown detail)
  - Confiança: 🟢

- [ ] T-19, Catálogo de obstáculos e `Obstacles_Scene_Props` com enum dinâmico **com cache das strings**
  - Origem no legado: `hb_props_obstacles.py:16-265`
  - Critério de pronto: RF-18; limites RN-33; itens do enum mantidos em lista de módulo
  - Confiança: 🟢

- [ ] T-20, Fachada `units.py` sobre `data/units.py`
  - Origem no legado: `units.py:2-19`, `data/units.py:9-124`
  - Critério de pronto: RF-22
  - Confiança: 🟢

### Bloco F — Operadores gerais

- [ ] T-21, `set_recommended_settings` com `bl_options = {'REGISTER', 'UNDO'}`
  - Origem no legado: `ops.py:29-116`
  - Critério de pronto: RF-23; Ctrl+Z desfaz
  - Confiança: 🟢

- [ ] T-22, `create_camera` com backplate emissivo dimensionado pelo FOV, **sem** `Material.use_nodes = True`
  - Origem no legado: `ops.py:270-490`
  - Critério de pronto: RF-24; `check_api.py` sem avisos de `use_nodes`
  - Confiança: 🟢

- [ ] T-23, `apply_settings_to_all` resolvendo inputs por nome (`Tick Length`, `Line Thickness`, `Text Size`) e
      aceitando cotas `CURVE`
  - Origem no legado: `ops.py:119-192`
  - Critério de pronto: cotas existentes recebem os novos tamanhos; nenhum `Socket_N` no código
  - Confiança: 🟡 (mapeamento `Socket_3/4/5` → nome a confirmar, Q-03)

- [ ] T-24, Modal `set_scale_with_two_points` com `{'REGISTER', 'UNDO'}`, `cancel()` e remoção do draw handler em `unregister()`
  - Origem no legado: `ops.py:494-652`
  - Critério de pronto: RF-25; desativar o add-on com o modal ativo não deixa handler órfão
  - Confiança: 🟢

- [ ] T-25, Decidir destino de `rendering_settings` (execute vazio) e `to_do`
  - Origem no legado: `ops.py:10-27,197-265`
  - Critério de pronto: decisão registrada (manter como diálogo ou remover)
  - Confiança: 🔴 (Q-06)

## Tarefas de Teste

- [ ] TT-01, Happy path de `GeoNodeObject`: criar, escrever/ler inputs, criar driver (Blender `--background`, `tests/blender_smoke.py`)
- [ ] TT-02, `set_input` com input inexistente → `ValueError`
- [ ] TT-03, Calculadora: iguais, excluído, fixos > total (valor negativo + aviso)
- [ ] TT-04, `run_calc_fix_until_stable`: convergência e −1
- [ ] TT-05, Paredes: propagação de `Length`, vizinhos com/sem `include_loop_seam`, cadeia fechada termina
- [ ] TT-06, `set_decimal` para mm/cm/m/in/ft (tabela de RN-19)
- [ ] TT-07, `set_main_scene` e `get_main_scene` em contexto de desenho (sem exceção)
- [ ] TT-08, `register()`/`unregister()` duas vezes seguidas sem resíduo (`driver_namespace`, ponteiros, handlers)
- [ ] TT-09, Abrir `.blend` salvo no 5.1 com drivers de input GN (cobre Q-02)

## Tarefas de Migração de Dados

- [ ] TM-01, Reescrever caminhos de driver `modifiers["M"]["ID"]` → `modifiers["M"].properties.inputs.ID.value` em
      `load_post` quando o arquivo vier de versão < 5.2
  - Origem: `hb_utils.py:55-60`
  - Confiança: 🔴 (Q-02 — confirmar se o Blender já migra sozinho)
- [ ] TM-02, Preservar ID custom props de prompts e marcadores (`IS_*`, `MENU_ID`) — não migrar para `bpy.props`
  - Confiança: 🟢

## Ordem Sugerida
1. **Bloco A** primeiro: toda a camada legada (49 arquivos) passa por `set_input`/`get_input`.
2. **Bloco B** e **T-09** em seguida: sem `GeoNodeObject` e `Object.home_builder` nada mais cria objetos.
3. **Bloco C** (calculadora e reavaliação) antes de qualquer biblioteca de produto.
4. **Bloco D** e **Bloco E** podem correr em paralelo.
5. **Bloco F** por último: operadores independentes, sem consumidores internos.
6. Bloqueios: T-15 depende de Q-04; T-23 depende de Q-03; TM-01 depende de Q-02.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 1 (2026-09-30) — ver **Decisões da rodada 1** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Interfaces dos node groups `.blend`.
- Q-02 Migração de caminhos de driver < 5.2.
- Q-03 Mapeamento `Socket_3/4/5` da cota.
- Q-04 Destino de `assign_materials`.
- Q-05 Destino dos botões `pc_prompts.*` da calculadora.
- Q-06 Destino de `rendering_settings`/`to_do`.

## Decisões da rodada 1 (2026-09-30)

Respostas em [`questions.md`](questions.md); fonte: `.reversa/respostas-questions.md`, investigações no Blender 5.2.0 e RAG do Manual Promob.

| Pergunta | Decisão | Efeito nas tarefas |
|---|---|---|
| Q-01 | Interfaces extraídas em [`node-group-interfaces.md`](node-group-interfaces.md) | Pré-requisito cumprido; T-01, T-07, T-08 e T-16 desbloqueadas 🟢 |
| Q-02 | 5.2 não aceita o caminho antigo; driver antigo fica inválido (valor 0) | **TM-01 confirmada** (reescrever em `load_post`, idempotente) 🟡; TT-09 usa um fcurve antigo criado com `animation_data.drivers.new(caminho_antigo)` |
| Q-03 | `Socket_3/4/5` **não** são Text Size/Tick Length/Line Thickness (bug) | T-23 🟢: escrever por nome *Text Size* (`Input_9`), *Tick Length* (`Socket_5`), *Line Thickness* (`Input_6`) e filtrar `CURVE` |
| Q-04 | Inputs reais = os de `update_wall_material` | T-15 🟢: **remover** `assign_materials` |
| Q-05 | Implementar os botões da calculadora | **Nova T-26**: operadores de calculadora (adicionar prompt, editar, rodar) com `{'REGISTER','UNDO'}` e `bl_idname` `btm.*`, ligados à UI de `Calculator.draw` |
| Q-06 | Remover `to_do`; `rendering_settings` vira painel | T-25 🟢 decidida |
| Q-07 | Default brasileiro (2,60 m / 150 mm / 800×2100 / 1200×1000 a 1100) | **Nova T-27**: presets de cena BR (padrão) e EUA, alternáveis (ver `product_common` Q-06); T-13 recalcula com os valores do preset |
| Q-08 | Unidade = `btm_settings.btm_unit`; sem pés | T-16 🟢: `get_unit_type` e `set_decimal` leem `btm_unit` |
| Q-09 | Limitar a 0 + aviso | T-11 🟢: clamp em 0 e aviso na UI (não só aviso) |
| Q-10 | Mover `HB_Wall_Editor_Props` | **Nova T-28**: mover para a unit `wall_editor`, mantendo `Scene.hb_wall_editor` |
| Q-11 | Limpeza opcional + seção de autoria | **Nova T-29**: painel "Autoria do projeto" com blocos Cliente × Empresa/Profissional (dados da empresa persistentes em `extension_path_user`), operador "Limpar dados do cliente" e aviso ao compartilhar |
| Q-12 | Catálogo de obstáculos BR em mm | T-19 🟢 + **nova T-30**: substituir a lista por tomada 4×2/4×4, interruptor, água fria/quente, esgoto, gás, registro, quadro de luz, luminária, coluna/viga |
