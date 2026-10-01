# hb_layouts — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Sequência para reimplementar a unit na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md) e [`design.md`](design.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Pré-requisitos
- [ ] Unit [`hb_core`](../hb_core/) disponível (`GeoNodeObject`, `GeoNodeDimension`, `GeoNodeRectangle`, `hb_utils`).
- [ ] Props de cena `hb_layout_scale`, `hb_paper_size`, `hb_paper_landscape`, `hb_lineart_*` registradas (hoje em `operators/layouts.py:4665-4718`).
- [ ] `paper_to_world` extraído para um módulo sem ciclo (ex.: `data/paper.py`) — hoje import tardio de `operators.layouts`.
- [ ] Assinaturas conferidas no RAG: `bpy.types.FreestyleLineSet`, `bpy.types.GreasePencilLineartModifier`,
      `bpy.types.AssetShelf.asset_poll`, `bpy.data.libraries.write`, `bpy.types.Context.temp_override`.

## Tarefas

### Bloco A — Papel e cena base

- [ ] T-01, Unificar a tabela de papéis (`PAPER_SIZES` e `operators/layouts.PAPER_SIZES_INCHES`) num único módulo e acrescentar papéis ABNT (A2, A1, A0)
  - Origem no legado: `hb_layouts.py:12-42`, `operators/layouts.py:90`
  - Critério de pronto: uma só fonte; RF-02; A4/A3 com resolução correta
  - Confiança: 🟢 (unificação) / 🔴 (lista final, Q-04)

- [ ] T-02, Unificar os padrões de papel (LETTER/TABLOID/LEGAL) numa só constante lida da preferência
  - Origem no legado: `hb_layouts.py:1448,2206`; `operators/layouts.py:4707-4718`; `__init__.py:132-141`
  - Critério de pronto: toda vista nova usa `default_paper_size`
  - Confiança: 🟢

- [ ] T-03, `LayoutView.create_scene` sem depender de `window.scene` quando não houver janela (usar `temp_override` ou retornar a cena sem ativá-la)
  - Origem no legado: `hb_layouts.py:1141-1192`
  - Critério de pronto: `create_scene` roda em `--background`
  - Confiança: 🟢

- [ ] T-04, Render de prancha e collections de roteamento
  - Origem no legado: `hb_layouts.py:1194-1272`
  - Critério de pronto: RF-01
  - Confiança: 🟢

- [ ] T-05, `LayoutView.delete` removendo collections `<cena>_*`, câmera, câmera jitter e GP
  - Origem no legado: `hb_layouts.py:1417-1424`
  - Critério de pronto: após excluir, nenhum datablock `<cena>_*` resta (`bpy.data.orphans_purge` não necessário)
  - Confiança: 🟡

### Bloco B — Traço

- [ ] T-06, Freestyle: linesets Solid/Dashed
  - Origem no legado: `hb_layouts.py:1274-1321`
  - Critério de pronto: RF-03
  - Confiança: 🟢

- [ ] T-07, Line Art: GP, camadas, 4 modificadores, câmera jitter, espessuras por escala; registrar exceção em `update_line_art_sizes` em vez de engolir
  - Origem no legado: `hb_layouts.py:132-252,349-515`
  - Critério de pronto: RF-04; mudar `hb_layout_scale` atualiza espessura
  - Confiança: 🟢

- [ ] T-08, Bake/unbake do Line Art
  - Origem no legado: `hb_layouts.py:198-346`
  - Critério de pronto: RF-14; cenários de bake passam
  - Confiança: 🟢

- [ ] T-09, Decidir destino do canal Marked, holdout de texto e vista híbrida iso (implementar o exportador ou remover)
  - Origem no legado: `hb_layouts.py:518-937`
  - Critério de pronto: decisão registrada; se mantidos, um chamador e testes
  - Confiança: 🔴 (Q-01)

### Bloco C — Vistas

- [ ] T-10, `ElevationView.create` com cotas automáticas incluindo closets (`IS_CLOSET_STARTER_CAGE`) e limiar de "superior" configurável
  - Origem no legado: `hb_layouts.py:1425-1735`
  - Critério de pronto: RF-05; cenários de elevação passam
  - Confiança: 🟢 (paridade) / 🟡 (inclusão de closets, Q-05)

- [ ] T-11, Enquadramento respeitando a razão de aspecto do papel (`ortho_scale` pelo eixo limitante)
  - Origem no legado: `hb_layouts.py:1504-1578`
  - Critério de pronto: conteúdo alto em papel paisagem não é cortado
  - Confiança: 🟡

- [ ] T-12, `ElevationView.update` usando a mesma regra de `_fit_camera_to_content`
  - Origem no legado: `hb_layouts.py:1780-1801`
  - Critério de pronto: atualizar e criar produzem o mesmo quadro
  - Confiança: 🟢

- [ ] T-13, `create_all_elevations` limitado às paredes da cena de cômodo atual
  - Origem no legado: `hb_layouts.py:2998-3006`
  - Critério de pronto: não cria elevações de outros cômodos
  - Confiança: 🟡

- [ ] T-14, `PlanView` com bbox considerando espessura de parede e gabinetes
  - Origem no legado: `hb_layouts.py:1819-1903`
  - Critério de pronto: RF-08; gabinetes que passam da parede aparecem no quadro
  - Confiança: 🟡

- [ ] T-15, `View3D`
  - Origem no legado: `hb_layouts.py:1986-2087`
  - Critério de pronto: RF-09
  - Confiança: 🟢

- [ ] T-16, `MultiView` (cruz, linhas ocultas, instâncias com rotação cancelada)
  - Origem no legado: `hb_layouts.py:2170-2396,2690-2958`
  - Critério de pronto: RF-10
  - Confiança: 🟢

- [ ] T-17, Iso-left com escadas de escala imperiais **e** métricas (1:20, 1:25, 1:50, 1:75, 1:100)
  - Origem no legado: `hb_layouts.py:2397-2668`
  - Critério de pronto: RF-11; em cena métrica usa escala métrica
  - Confiança: 🟢 (paridade) / 🔴 (escada métrica, Q-04)

- [ ] T-18, Remover código morto (`PlanView/View3D._fit_camera_to_content`, `MultiView._calculate_grid`, `_create_view_label`)
  - Origem no legado: `hb_layouts.py:1904,2088,2860,2933`
  - Critério de pronto: grep sem referências; testes verdes
  - Confiança: 🟢

- [ ] T-19, `get_layout_view_from_scene` e atalhos `create_*`
  - Origem no legado: `hb_layouts.py:2960-3017`
  - Critério de pronto: RF-15
  - Confiança: 🟢

### Bloco D — Carimbo

- [ ] T-20, `TitleBlock` com fonte de fallback multiplataforma e campos preenchidos de `Scene.hb_project` (nome, projetista, escala, página N de M); `update()` funcional
  - Origem no legado: `hb_layouts.py:44-48,967-1107`
  - Critério de pronto: RF-12/RF-13; mudar o nome do projeto atualiza todos os carimbos
  - Confiança: 🔴 (formato do carimbo, Q-03)

### Bloco E — Detalhes 2D

- [ ] T-21, `DetailView` e primitivas sem `Material.use_nodes = True`; `_setup_2d_view` tolerante à ausência de `context.screen`
  - Origem no legado: `hb_details.py:11-305,384-439`
  - Critério de pronto: RF-17; `check_api.py` limpo
  - Confiança: 🟢

- [ ] T-22, Fonte do rótulo: `annotation_font` > fonte embarcada na extensão > Bfont (sem depender de `%WINDIR%`)
  - Origem no legado: `hb_details.py:308-381`
  - Critério de pronto: mesmo resultado em Linux/Windows/macOS
  - Confiança: 🟡

- [ ] T-23, Biblioteca de detalhes: escrita atômica do índice (arquivo temporário + rename), carga sem `bpy.ops`, exclusão que reporta falha real
  - Origem no legado: `hb_detail_library.py:14-243`
  - Critério de pronto: RF-18/RF-19; índice nunca fica truncado; excluir arquivo inexistente reporta aviso
  - Confiança: 🟢

- [ ] T-24, Miniaturas dos detalhes (render do quadro da cena ou `asset_generate_preview`)
  - Origem no legado: docstring de `hb_detail_library.py` (não implementado)
  - Critério de pronto: cada entrada tem uma prévia
  - Confiança: 🔴 (Q-06)

### Bloco F — Assets

- [ ] T-25, `ensure_asset_libraries` / limpeza de órfãs / subpastas / catálogos
  - Origem no legado: `hb_assets.py:9-246`
  - Critério de pronto: RF-20/RF-21/RF-22
  - Confiança: 🟢

- [ ] T-26, `asset_poll` com guarda para `None`; `register/unregister` pela lista de classes (sem `hasattr(bpy.types, …)`)
  - Origem no legado: `hb_assets.py:323-339,408-428`
  - Critério de pronto: recarregar a extensão 2× sem erro nem operadores duplicados
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, `get_paper_resolution` para todos os papéis, retrato/paisagem, DPI 150/300
- [ ] TT-02, Elevação: parede vazia, inferiores + aéreos, gabinete fora da parede (não cotado)
- [ ] TT-03, Planta sem paredes e com paredes
- [ ] TT-04, Multivista: `views=[]` → `None`; cruz com 5 vistas; origem girada 90°
- [ ] TT-05, Line Art: criar, mudar escala, bake/unbake
- [ ] TT-06, Biblioteca de detalhes: salvar, listar, carregar, excluir, índice corrompido
- [ ] TT-07, Assets: registro limpo, órfãs removidas, recarga sem vazamento
- [ ] TT-08, Smoke `--background`: criar elevação e planta sem janela (após T-03)

## Tarefas de Migração de Dados

- [ ] TM-01, Cenas de layout antigas sem `HB_LINE_ENGINE` continuam tratadas como FREESTYLE. 🟢
- [ ] TM-02, Se T-01 renomear chaves de papel, mapear `PAPER_SIZE` antigo (LETTER/LEGAL/TABLOID/A4/A3) → novo. 🟡
- [ ] TM-03, Entradas antigas de `library_index.json` sem `is_crown_detail` tratadas por `detail_type`. 🟡

## Ordem Sugerida
1. **Bloco A** (papel, cena base) → **Bloco B** (traço): toda vista depende deles.
2. **Bloco C** na ordem T-10 → T-11/T-12 → T-14 → T-15 → T-16 → T-17 → T-19; T-18 ao final.
3. **Bloco D** depois de `hb_core` expor `Scene.hb_project`.
4. **Bloco E** e **Bloco F** em paralelo, independentes das vistas.
5. Bloqueios: T-09 (Q-01), T-20 (Q-03), T-01/T-17 (Q-04), T-10 (Q-05), T-24 (Q-06).

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 1 (2026-09-30) — ver **Decisões da rodada 1** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md).

## Decisões da rodada 1 (2026-09-30)

Respostas em [`questions.md`](questions.md); fonte: `.reversa/respostas-questions.md`, investigações no Blender 5.2.0 e RAG do Manual Promob.

| Pergunta | Decisão | Efeito nas tarefas |
|---|---|---|
| Q-01 | Remover o exportador híbrido | T-09 🟢: remover (~420 linhas); T-18 inclui esse código |
| Q-02 | Freestyle + modos de linha do Promob | T-06 🟢 + **nova T-27**: modos *Hide*, *Hide PB*, *Sem Preenchimento*, *com Linhas*; paredes 4 px, demais 2 px |
| Q-03 | Legenda NBR em protótipos de impressão | T-20 🟢 + **nova T-28**: protótipos de prancha salvos/reutilizáveis com campos de Cliente/Empresa, Data e Hora e indicadores de vista |
| Q-04 | ABNT A4–A0 + escalas métricas; imperiais mantidas | T-01 e T-17 🟢 |
| Q-05 | Cotas de closets; classificar pelo tipo | T-10 🟢: classificação por `CABINET_TYPE`, sem limiar de 1,2 m |
| Q-06 | Render automático ao salvar | T-24 🟢 |
| Q-07 | Respeitar o aspecto, com escala explícita | T-11 🟡: a escala escolhida manda; enquadramento sem distorção |
| Q-08 | Cômodo atual com seleção de paredes | T-13 🟢 ampliada: diálogo com paredes pré-selecionadas (as que têm módulos), distância de cotagem, escala, altura de corte 800 mm e planta baixa opcional |
| Q-09 | Fonte livre embarcada, configurável por texto | T-22 🟢 |
