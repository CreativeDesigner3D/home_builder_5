# product_common — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Pré-requisitos
- [ ] Unit [`hb_core`](../hb_core/) disponível: `GeoNodeCage`, `GeoNodeObject`, `GeoNodeCutpart`, `add_property`,
      DSL de drivers (ver `hb_core/tasks.md`, blocos A–C).
- [ ] `GeoNodeText` de [`hb_layouts`](../hb_layouts/) disponível.
- [ ] Ponte de inputs GN consolidada em `compat.py` (`hb_core` T-01); esta unit não deve usar `hb_utils` direto.
- [ ] Assets `face_frame/face_frame_assets/door_profiles/<Categoria> Profiles/*.blend` presentes.
- [ ] Decisão de mercado registrada (Q-06): manter padrões americanos em polegadas ou parametrizar para MDF/MDP BR.
- [ ] Assinaturas confirmadas no RAG (`python3 docs/rag/tools/rag_search.py --symbol …`) e
      `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`.

## Tarefas

### Bloco A — Layout paramétrico da porta (Python puro, sem `bpy`)

- [ ] T-01, `DOOR_STYLE_FALLBACK` e `door_style_info(style)` como `dict` desacoplado do RNA
  - Origem no legado: `product_libraries/common/door_builder.py:36-95`
  - Critério de pronto: `door_style_info(None)` devolve cópia (mutá-la não altera o fallback); campos ausentes no
    estilo caem no padrão
  - Confiança: 🟢

- [ ] T-02, `_frame_widths` com pisos 1/2" (uniformes) e 0.0 (overrides por lado)
  - Origem no legado: `product_libraries/common/door_builder.py:52-55`, `:69-84`
  - Critério de pronto: `stile_width = 0,2"` → 1/2"; `left_stile_width = 0.0` → 0.0; `None` → uniforme
  - Confiança: 🟢

- [ ] T-03, `layout_min_size` com k efetivo de mid rails
  - Origem no legado: `product_libraries/common/door_builder.py:98-110`
  - Critério de pronto: fallback → (6,5", 6,5"); com `add_mid_rail` → `min_h` 9,5"; SLAB → (0, 0)
  - Confiança: 🟢

- [ ] T-04, `door_layout` com pares `(coef, offset)`: membros, k mid rails, m mid stiles segmentados, painéis
  - Origem no legado: `product_libraries/common/door_builder.py:113-212`
  - Critério de pronto: precedência RN-05 respeitada; para qualquer W, H ≥ mínimo, as peças cobrem o retângulo sem
    sobreposição (teste de propriedade)
  - Confiança: 🟢

- [ ] T-05, `evaluate_layout` (realizador estático) e `shape_rise`
  - Origem no legado: `product_libraries/common/door_builder.py:215-227`, `:576-582`
  - Critério de pronto: `x0 < x1`, `z0 < z1` dentro de [0, W] × [0, H]; `shape_rise('ARCH', 12")` = 2,25"
  - Confiança: 🟢

### Bloco B — Geometria da porta

- [ ] T-06, Primitivas geométricas: `_cell_perimeter` (meia-esquadria), `_resample_loop`, `_clip_half`
      (Sutherland-Hodgman), `_shape_curve_pts` (arco circular e ogiva Crown)
  - Origem no legado: `product_libraries/common/door_builder.py:324-346`, `:585-675`
  - Critério de pronto: testes unitários puros (sem `bpy`); retângulo → direções `(±1, ±1)`; rise ≤ 1e-6 → `None`
  - Confiança: 🟢

- [ ] T-07, `build_door_mesh` — orquestração, caixas simples e cadeia de fallback por peça
  - Origem no legado: `product_libraries/common/door_builder.py:1202-1362`
  - Critério de pronto: com todas as seções `None`, gera só caixas; nenhum emissor levanta exceção; peças de
    largura 0 são puladas
  - Confiança: 🟢

- [ ] T-08, Escrita da malha: `from_pydata`, `materials.clear()` + tripla, atributo `material_index` `INT`/`FACE`
  - Origem no legado: `product_libraries/common/door_builder.py:1389-1404`
  - Critério de pronto: faces com slots 0/1/2 conforme RN-09; confirmar `Mesh.attributes.new` e `foreach_set` no RAG
  - Confiança: 🟢

- [ ] T-09, Borda externa perfilada (`_emit_edge_profiled_box`) só nos lados do contorno
  - Origem no legado: `product_libraries/common/door_builder.py:1054-1119`
  - Critério de pronto: lados internos com u=0; `u_max` maior que a peça → borda reta
  - Confiança: 🟢

- [ ] T-10, Painel raised e ranhurado (BEAD/KERF), com tampas planas em células arqueadas
  - Origem no legado: `product_libraries/common/door_builder.py:447-571`, `:1314-1317`
  - Critério de pronto: RN-12 e RN-13 verificadas; raise com ranhura → ranhura ignorada
  - Confiança: 🟢

- [ ] T-11, Arcos: `_emit_shaped_panel`, `_emit_shaped_rail` (TOP/BOTTOM), Double e Twin
  - Origem no legado: `product_libraries/common/door_builder.py:801-840`, `:1122-1199`, `:1263-1298`
  - Critério de pronto: perfil externo descartado quando não cabe acima do pico (RN-16); célula ≤ 2" sem arco
  - Confiança: 🟢

- [ ] T-12, Sticking e moldura aplicada (`_emit_strip_rings`, `applied_scope` ALL/RAILS)
  - Origem no legado: `product_libraries/common/door_builder.py:349-443`, `:1363-1384`
  - Critério de pronto: fallback cruzado rail/stile; célula pequena pula o strip; RAILS só topo/base
  - Confiança: 🟢

- [ ] T-13, Mullions retos (GRID, MISSION, PRAIRIE, X) e curvos (GOTHIC, DBL_GOTHIC, DBL_BOW, INTERLOKEN)
  - Origem no legado: `product_libraries/common/door_builder.py:678-1051`
  - Critério de pronto: tabelas de RN-19/RN-20; escalonamento 0,2 mm nos curvos; recorte sob a curva
  - Confiança: 🟢

- [ ] T-14, Construção MITERED (`build_mitered_frame`)
  - Origem no legado: `product_libraries/common/door_builder.py:250-321`, `:1249-1253`, `:1385-1388`
  - Critério de pronto: 4 lados com `max(u)`; sem mid rail, arco, sticking e applied; mullion aplicado
  - Confiança: 🟢

### Bloco C — Biblioteca de perfis

- [ ] T-15, `load_profile` com cache `(path, mtime, res)`, amostragem Bézier e limpeza em `finally`
  - Origem no legado: `product_libraries/common/door_profiles.py:27-150`
  - Critério de pronto: segunda carga não chama `libraries.load`; nenhum objeto/curva órfão após a carga;
    `FileNotFoundError`/`ValueError` nos casos de RN-28
  - Confiança: 🟢

- [ ] T-16, Remover datablocks órfãos também de materiais trazidos pelo append (ou carregar só curvas)
  - Origem no legado: `product_libraries/common/door_profiles.py:105-126`
  - Critério de pronto: contagem de `bpy.data.materials`/`curves` igual antes e depois de carregar um perfil novo
  - Confiança: 🟡

- [ ] T-17, Conversores de seção: `edge_profile_section`, `sticking_section`/`sticking_strip`,
      `panel_profile_section`, `applied_strip`, `member_section`, `profile_from_object`
  - Origem no legado: `product_libraries/common/door_profiles.py:153-610`
  - Critério de pronto: RN-23..RN-27; desenho ilegível → `None`
  - Confiança: 🟢

- [ ] T-18, Perfis de borda de catálogo gerados em código (`named_edge_section`)
  - Origem no legado: `product_libraries/common/door_profiles.py:613-677`
  - Critério de pronto: 7 nomes resolvem (case-insensitive, `strip()`); desconhecido → `None`
  - Confiança: 🟢

### Bloco D — Eletrodomésticos

- [ ] T-19, `Appliance.create_appliance` com marcadores, `Mirror Y`, texto filho e drivers
  - Origem no legado: `product_libraries/common/types_appliances.py:8-51`
  - Critério de pronto: cenário "Criar fogão" de `requirements.md`
  - Confiança: 🟢

- [ ] T-20, 10 subclasses com dimensões, `variable_width`, `IS_COUNTERTOP_APPLIANCE` e variantes
  - Origem no legado: `product_libraries/common/types_appliances.py:54-220`
  - Critério de pronto: tabela de RN-29..RN-33
  - Confiança: 🟢

- [ ] T-21, Tratar prompts de texto de Hood ("Hood Style") e Sink ("Sink Type"), trocando por `COMBOBOX` ou
      suportando `'TEXT'` em `add_property`
  - Origem no legado: `product_libraries/common/types_appliances.py:176`, `:192`; `hb_props.py:335-374`
  - Critério de pronto: propriedades existem após `create`
  - Confiança: 🔴 (Q-08)

### Bloco E — Coifas de madeira

- [ ] T-22, Carcaça, limpeza preservando `IS_MANUAL_PART` e despacho por estilo
  - Origem no legado: `product_libraries/common/wood_hoods.py:29-39`, `:74-203`, `:1526-1541`, `:1762-1770`
  - Critério de pronto: RN-35, RN-36, RN-45; estilo desconhecido → BOX
  - Confiança: 🟢

- [ ] T-23, Estilos retos com drivers (SHELF, NICHE, MANTLE, PLANTATION, GRAND_MANTLE, painéis frontais)
  - Origem no legado: `product_libraries/common/wood_hoods.py:91-276`
  - Critério de pronto: redimensionar o cage atualiza as peças sem reconstruir; RN-37
  - Confiança: 🟢

- [ ] T-24, Estilos inclinados e shiplap estáticos (`_build_angled`, `_FrontProfile`, `_wrap_shiplap`)
  - Origem no legado: `product_libraries/common/wood_hoods.py:279-358`, `:1082-1219`
  - Critério de pronto: RN-38, RN-43; malha reconstruída ao mudar dimensões pelo diálogo
  - Confiança: 🟢

- [ ] T-25, Estilo CUSTOM: opções com limites, migração `panel_rail_width`, quadro frontal com baias, paneled ends,
      liner com recorte de exaustor, moldura de mantle
  - Origem no legado: `product_libraries/common/wood_hoods.py:365-1016`, `:1222-1499`
  - Critério de pronto: RN-39..RN-44, RN-48; valores fora dos limites são grampeados
  - Confiança: 🟢

- [ ] T-26, Acabamento e sobreposição via face frame com import tardio protegido
  - Origem no legado: `product_libraries/common/wood_hoods.py:426-489`, `:1544-1632`
  - Critério de pronto: sem o face frame, a coifa é construída com sobreposição de 1/2" e sem erro
  - Confiança: 🟢

- [ ] T-27, Operadores `blendertomob.build_wood_hood` e `blendertomob.wood_hood_prompts`
  - Origem no legado: `product_libraries/common/wood_hoods.py:1773-2066`
  - Critério de pronto: `poll` só em HOOD; `UNDO` registrado; `check()` reconstrói; textos de UI em português
  - Confiança: 🟢

- [ ] T-28, Substituir as anotações dinâmicas `bay_front_1..10` por declaração explícita (ou `CollectionProperty`)
  - Origem no legado: `product_libraries/common/wood_hoods.py:1920-1924`
  - Critério de pronto: registro funciona com anotações preguiçosas (PEP 649)
  - Confiança: 🟡 (Q-03)

- [ ] T-29, Snapshot/restore e operador `blendertomob.revert_hood_part`, usando `compat.gn_input_data_path`
  - Origem no legado: `product_libraries/common/wood_hoods.py:41-54`, `:1635-1759`, `:2193-2226`
  - Critério de pronto: peça editada volta a seguir o cage; drivers válidos em 5.2; flags removidos
  - Confiança: 🟡 (Q-04)

### Bloco F — Registries

- [ ] T-30, `accessory_registry` tolerante a falha, com consultas derivadas
  - Origem no legado: `accessory_registry.py:1-117`
  - Critério de pronto: provider com exceção → `[]` + mensagem; `all_items` injeta `host`
  - Confiança: 🟢

- [ ] T-31, `appliance_spec_registry` de provider único
  - Origem no legado: `appliance_spec_registry.py:1-32`
  - Critério de pronto: `get_provider()` → `None` sem registro; segundo registro substitui
  - Confiança: 🟢

- [ ] T-32, Definir o contrato dos providers (formato de `spec.panels`) ou retirar os registries
  - Origem no legado: `face_frame/operators/ops_appliance_panels.py:518-545`, `face_frame/operators/ops_cabinet.py:2296-2972`
  - Critério de pronto: contrato documentado e um provider de exemplo, ou remoção decidida
  - Confiança: 🔴 (Q-01)

## Tarefas de Teste

- [ ] TT-01, Testes puros (sem Blender) de `door_layout`, `layout_min_size`, `shape_rise`, `_mullion_layout`,
      `_clip_half` — cobrem os cenários de layout de `requirements.md`
- [ ] TT-02, `build_door_mesh` em `--background`: SLAB, 5 peças, MITERED, raised, arco, mullion GRID; checar slots
- [ ] TT-03, Fallbacks: todas as seções `None`, painel sem profundidade, célula ≤ 2" arqueada
- [ ] TT-04, `load_profile`: cache por mtime, `FileNotFoundError`, ausência de datablocks órfãos
- [ ] TT-05, `named_edge_section` para os 7 nomes e um desconhecido
- [ ] TT-06, Eletrodomésticos: dimensões das 10 classes e variantes (RN-29..RN-32)
- [ ] TT-07, Coifa: cada um dos 14 estilos constrói sem exceção; troca de estilo preserva `IS_MANUAL_PART`
- [ ] TT-08, Coifa sem face frame (import falhando) constrói com sobreposição 1/2"
- [ ] TT-09, Snapshot em arquivo salvo no 5.1 e restore no 5.2
- [ ] TT-10, Registries: provider com falha, sem provider, sobrescrita
- [ ] TT-11, `register()`/`unregister()` de `wood_hoods` duas vezes sem resíduo (extensão do `tests/blender_legacy_smoke.py`)

## Tarefas de Migração de Dados

- [ ] TM-01, Migrar `panel_rail_width` → `panel_top_rail_width` e `panel_bottom_rail_width` ao ler `WOOD_HOOD_CUSTOM_OPTS`
  - Origem: `product_libraries/common/wood_hoods.py:501-505`
  - Confiança: 🟢
- [ ] TM-02, Migrar caminhos de driver em `HOOD_PARAMETRIC_SNAPSHOT` salvos em < 5.2
  - Origem: `product_libraries/common/wood_hoods.py:46-54`
  - Confiança: 🟡 (Q-04)
- [ ] TM-03, Preservar as ID props de eletrodoméstico e coifa (`IS_APPLIANCE`, `APPLIANCE_TYPE`, `WOOD_HOOD_*`,
      `IS_WOOD_HOOD_PART`, `IS_MANUAL_PART`) — não migrar para `bpy.props`
  - Confiança: 🟢

## Ordem Sugerida
1. **Bloco A** primeiro: Python puro, testável sem Blender, e base para portas e coifas.
2. **Bloco C** em paralelo com o início do **Bloco B**: as seções são entrada de `build_door_mesh`.
3. **Bloco B** completo antes do consumidor `face_frame` (frentes de armário).
4. **Bloco D** depende só de `hb_core`/`hb_layouts`; pode correr em paralelo com A–C.
5. **Bloco E** depois de A (usa `door_layout`) e D (cage HOOD).
6. **Bloco F** por último; T-32 bloqueado por Q-01.
7. Bloqueios: T-21 ← Q-08; T-27 ← Q-10; T-28 ← Q-03; T-29/TM-02 ← Q-04, Q-09; pré-requisito de mercado ← Q-06;
   escopo dos blocos B e E ← Q-11.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 1 (2026-09-30) — ver **Decisões da rodada 1** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Contrato e existência de providers de acessórios/specs.
- Q-02 Destino do asset `Generic Trash Pullout.blend`.
- Q-03 Versão do Python do Blender 5.2 (anotações dinâmicas).
- Q-04 `driver_add` em caminho `.properties.inputs.X.value` e cobertura da migração de snapshot.
- Q-05 Mínimo de porta: +1/2" ou +1".
- Q-06 Padrões americanos (polegadas, 3/4", CWP) × marcenaria brasileira.
- Q-07 Builders dedicados para PENINSULA e PLANTATION.
- Q-08 Prompts de texto de coifa e pia.
- Q-09 Revert apagar modificadores do usuário.
- Q-10 Cancelar o diálogo de opções da coifa.
- Q-11 Subconjunto de estilos/mullions/perfis relevante para o mercado brasileiro.

## Decisões da rodada 1 (2026-09-30)

Respostas em [`questions.md`](questions.md); fonte: `.reversa/respostas-questions.md`, investigações no Blender 5.2.0 e RAG do Manual Promob.

| Pergunta | Decisão | Efeito nas tarefas |
|---|---|---|
| Q-01 | Registries como ponto de extensão para catálogos de fabricante | T-32 🟢: documentar o contrato e esconder menus sem provider (sem provider de exemplo) |
| Q-02 | Asset sem uso | **Nova T-33**: remover `Trash Pull Outs/Generic Trash Pullout.blend` do pacote 🟢 |
| Q-03 | Python 3.13.13 no 5.2.0 | T-28 vira **preventiva** 🟢 (hoje funciona) |
| Q-04 | `driver_add` no caminho 5.2 funciona | T-29 e TM-02 🟢 |
| Q-05 | Membros + 1" numa constante | T-03 🟢: `layout_min_size` passa a usar +1" (muda o limiar da coifa) |
| Q-06 | BR como padrão, alternável com EUA | Pré-requisito de mercado cumprido 🟢: espessuras e eletrodomésticos vêm do preset ativo |
| Q-07 | Tirar PENINSULA/SHIPLAP_PENINSULA/PLANTATION | T-22 🟢: lista com 11 estilos |
| Q-08 | Listas fixas de coifa e pia | T-21 🟢: `COMBOBOX` com as opções definidas |
| Q-09 | Preservar modificadores desconhecidos | T-29 🟡 |
| Q-10 | Cancelar restaura o estado | T-27 🟡: guardar no `invoke`, restaurar no `cancel` |
| Q-11 | Subconjunto de estética | Blocos B e E 🟢: BOX, reta com mantle, inclinada simples; lisa e Shaker; GRID; reto/chanfro/boleado. Demais tarefas desses blocos rebaixadas para `Could` |
