# face_frame — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#face_frame`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/face_frame/`.
> Namespace de operadores legado: `hb_face_frame.*`.

## Interface

### Modelo de dados 🟢

```
Object (cage raiz, IS_FACE_FRAME_CABINET_CAGE, CLASS_NAME, STYLE_NAME)
│   .face_frame_cabinet → Face_Frame_Cabinet_Props (+ mid_stile_widths[N−1], corner_sections)
├── peças de carcaça/moldura (hb_part_role, hb_segment_start_bay, hb_mid_stile_index)
└── bay cage (IS_FACE_FRAME_BAY_CAGE, hb_bay_index) .face_frame_bay
    └── árvore: split node (IS_FACE_FRAME_SPLIT_NODE, axis H/V) .face_frame_split (+ splitter_widths)
        └── opening (IS_FACE_FRAME_OPENING_CAGE) .face_frame_opening (+ interior_items, drawer_look_openings)
            ├── pivô → frente (porta/gaveta/…) → puxador      (recriados a cada recálculo)
            └── árvore interior (IS_INTERIOR_SPLIT_NODE / IS_INTERIOR_REGION)
Scene.hb_face_frame → Face_Frame_Scene_Props (cabinet_styles, door_styles, drawer_front_styles)
```

Propriedades são `bpy.props` lidas por atributo; metadados de identidade são ID properties. O vínculo
gabinete → estilo é **por nome** (`STYLE_NAME`, `props_hb_face_frame.py:1690`). 🟢

### Tipos (`types_face_frame.py`, `types_face_frame_corner.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `FaceFrameCabinet.create_cabinet_root` | `(name)` | — | Tags, `CLASS_NAME`, defaults de top_scribe/blind; escreve dims por último (`:966`) 🟢 |
| `FaceFrameCabinet.create_carcass` | `(bay_qty)` | — | Constrói tudo sob guardas e faz **um** `recalculate()` (`:1017`) 🟢 |
| `FaceFrameCabinet.recalculate` | `()` | — | Pipeline completo (`:1842-2531`) 🟢 |
| `recalculate_face_frame_cabinet` | `(obj)` | — | Entrada segura: sobe à raiz, respeita `suspend_recalc` e `_RECALCULATING` (`:8745-8777`) 🟢 |
| `suspend_recalc` | context manager | — | Coalesce recálculos por nome em `_PENDING_RECALC_NAMES` (`:81-107`) 🟢 |
| `WRAP_CLASS_REGISTRY` | `dict[CLASS_NAME → classe]` | — | Classes ausentes caem na base (`:8636-8680`) 🟢 |
| `_distribute_bay_widths` / `_redistribute_split_node` | `()` / `(node)` | — | Algoritmo A1 (`:1641`, `:1763`) 🟢 |
| merge / break | `(cab_a, cab_b)` / `(cab, gap)` | — | Fusão e quebra (`:9025`, `:9331`) 🟢 |
| Classes de canto | `corner_type` PIE_CUT / DIAGONAL / PIE_CUT_DRAWER | — | `recalculate` próprio (`types_face_frame_corner.py:981`); tipo desconhecido → `NotImplementedError` 🟢 |
| Produtos | `Leg`, `FloatingShelf`, `Valance`, `HalfWall`, `SupportFrame`, misc/door part | — | `recalculate` próprios (`:7649`, `:7927`, `:8065`) 🔴 |

### Solver (`solver_face_frame.py`, sem `bpy` de escrita)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `FaceFrameLayout` | `(obj)` | snapshot | Dims, espessuras, rodapé, stiles, bays, mid stiles, flags (`:33`) 🟢 |
| `_read_tree_node` | `(obj)` | `dict` | Nó split/leaf (`:272-335`) 🟢 |
| segmentos de rails/fundos/costas/travessas/kicks | `(layout)` | `list[Segment]` | Algoritmo A2 (`:1305-1456`) 🟢 |
| mid stiles | `(layout)` | `list` | RN-11 (`:1743-1809`) 🟢 |
| `bay_openings` / `_walk_tree` | `(layout, bay)` | leaf/splitter/backing rects | Algoritmo A3 (`:2993`) 🟢 |
| `front_leaves` | `(layout, leaf)` | `list[FrontLeaf]` | Algoritmo A4 (`:3593`) 🟢 |
| `auto_shelf_qty` | `(height, depth)` | `int` | A8 (`:3717-3765`) 🟢 |
| `compute_wedge` / `face_frame_angle` / `face_frame_length` | — | — | A6/A7 (`:1249`, `:1558`, `:1578`) 🟢 |

### Exposição, painéis e presets

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `exposure.recalc_cabinet_exposure` / `recalc_with_neighbors` / `recalc_all_cabinet_exposure` | `(cab_obj)` / `(cab_obj)` / `(context)` | — | A5; `_apply_side` escreve só lados com `*_finish_end_auto` (`exposure.py:218-476`, `:578`, `:619`) 🟢 |
| `applied_panel_sizing.*` | `(cab, side)` | larguras | A9 e RN-29 (`applied_panel_sizing.py:65-256`) 🟢 |
| `bay_presets.default_bay_config` / `operators/ops_cabinet.apply_bay_preset` | `(cabinet_name, bay_width)` / `(bay_obj, config, reset_bay_props=False)` | `dict` / — | Receitas L/H/V declarativas (`bay_presets.py:33-494`, `:392`; `operators/ops_cabinet.py:3081`) 🟢 |

### Operadores (13 módulos em `operators/`)

| Grupo | Exemplos | Observação |
|-------|----------|------------|
| Inserção | `hb_face_frame.place_cabinet` (modal, `ops_placement.py:1746`, `_finalize` `:3543`) | Raycast em paredes/ilhas/frentes; preview com `HB_CURRENT_DRAW_OBJ` 🟢 |
| Estrutura | draw/delete/join/break, equalize, `split_opening`, change opening/bay, insert/delete bay, interiores, acessórios, grupos | `ops_cabinet.py`; `split_preview` POST_VIEW 🟢 |
| Edição direta | grab de fronteiras (`op_modify_cabinet.py`), rótulos editáveis (`dim_edit_overlay.py`, POST_PIXEL permanente), comandos por peça (`ops_part_commands.py`) | 🟢 |
| Estilos/acabamentos | CRUD e pintura de estilos (`ops_styles.py`), `apply_finished_ends_to_exposed` (`ops_finished_ends.py`) | 🟢 |
| Outros | tampos (`ops_countertop.py`), painéis de eletro (`ops_appliance_panels.py`), cunha (`ops_wedge.py`), abrir frentes (`op_open_mode.py`), biblioteca, padrões, miniaturas | 🟢 |

## Fluxo Principal

### F1. Registro 🟢
`__init__.py:13-26`: props → menus → 13 módulos de operadores → UI → `dim_edit_overlay` (draw handler POST_PIXEL +
keymap). Cria `Object.face_frame_*`, `leg_product`, `floating_shelf`, `valance_product`, `Scene.hb_face_frame` e o
handler `load_post` `_seed_style_rename_anchors` (`props_hb_face_frame.py:8105-8155`).

### F2. Inserção 🟢
1. Modal com raycast em paredes, ilhas e frentes de fogão/bay; largura por fill-to-gap ou digitada.
2. `_auto_bay_qty = ceil((w − 1/16")/36")`, limitado a [1, 10] (`ops_placement.py:317`).
3. `_finalize`: `get_cabinet_class(nome)` → `cls().create(nome, bay_qty)` → `cab_props.width = largura` →
   `apply_bay_preset(default_bay_config(nome, largura_bay))` dentro de `suspend_recalc` →
   `_try_auto_merge_with_neighbor` → exposição.
4. Falha → `{'CANCELLED'}` com report.

### F3. Recálculo 🟢 (fluxograma `flowcharts/legacy-face_frame-recalculate.md`)
1. Callback de prop ou operador → `recalculate_face_frame_cabinet(obj)` → raiz.
2. Em `suspend_recalc`: enfileira o nome. Em recursão (`id(root)` em `_RECALCULATING`): sai.
3. `_wrap_cabinet` por `CLASS_NAME` → `recalculate()`:
   1. `Dim X/Y/Z` do cage;
   2. distribuições na ordem obrigatória: profundidades → alturas → kicks → rails → **larguras de bays** → árvores;
   3. `FaceFrameLayout`; segmentos de rails e reconciliação; fillers de front drop;
   4. se tem carcaça: fundos, costas, kick e retornos, blind panels, travessas (BASE/LAP) ou tampo (UPPER/TALL);
   5. despacho por `hb_part_role` dos filhos diretos (pula `IS_MANUAL_PART` ou sem GN); gira stiles/rails no modo angular;
      escreve location e `Length/Width/Thickness`;
   6. bays → `_update_bay_cage` → openings, frentes (recriadas), interiores;
   7. pós-passes: painéis aplicados, fundo acabado, flush-x, stiles full overlay, painéis texturizados, retornos,
      cortador angular, extensões; anotações, furniture top, hutch, cunha;
   8. reaplica estilo e destaques do modo de seleção; painel solto.

### F4. Árvore de aberturas 🟢 (fluxograma `flowcharts/legacy-face_frame-solver_walk_tree.md`)
1. Reveals da raiz do bay (cage maior que o vão da moldura).
2. Por nó: filhos travados mantêm o tamanho; destravados dividem o resto (vaidade +4").
3. Membros: mid rail/mid stile com largura padrão ou por membro; removidos colapsam (3/32"); promoção a BOTTOM_RAIL.
4. Backings: prateleira 3/4" (H) ou divisão (V) quando `add_backing`.
5. Saída em coordenadas do bay; folhas casadas por `obj_name`; splitters e backings recriados.

### F5. Frentes 🟢 (fluxograma `flowcharts/legacy-face_frame-front_leaves.md`)
Overlay efetivo por lado → tamanho = vão + overlays → pivô (dobradiça/slide) → folhas simples/duplas/triplas →
`hinge` para posicionar o puxador. A malha da porta vem do motor de [`product_common`](../product_common/design.md)
(`door_builder.build_door_mesh`) quando `USE_PYTHON_DOORS`.

### F6. Exposição 🟢 (fluxograma `flowcharts/legacy-face_frame-exposure.md`)
Faixas Z dos vizinhos coincidentes por lado → UNEXPOSED / PARTIAL / EXPOSED → acabamento e scribe automáticos só nos
lados com auto ligado (religado ao final, porque as próprias escritas o desligam).

### F7. Distribuição de bays 🟢 (fluxograma `flowcharts/legacy-face_frame-distribute_bay_widths.md`)
Disponível = largura − stiles de ponta − mid stiles − blind (ou hipotenusa) − travados; share igual entre destravados;
escrita sob `_DISTRIBUTING_WIDTHS` para não travar.

### F8. Segmentos de rail 🟢 (fluxograma `flowcharts/legacy-face_frame-rail_segments.md`)
Varredura dos gaps: abre segmento novo sempre que RN-09 falha; identidade por `hb_segment_start_bay`.

## Fluxos Alternativos

- **Classe fora do registro:** recalcula como `FaceFrameCabinet` → `_has_toe_kick()` False → rodapé zerado. 🟢/🟡
- **`corner_type` desconhecido:** `NotImplementedError`. 🟢
- **Travados maiores que o disponível:** bay destravado negativo, sem clamp. 🟡
- **`refrigerator_opening_height` escrito por `obj[...]`:** a `bpy.props` fica em 62" enquanto o inset usa 69". 🟢/🟡
- **Erro no dreno de `suspend_recalc`:** engolido. 🟢
- **Gabinete com rotação relativa à parede:** exposição assume X local da parede. 🟡
- **Split preview ativo no `unregister()`:** handler não removido. 🟢
- **Peça `IS_MANUAL_PART`:** fica fora da reescrita; pode ficar desalinhada da carcaça. 🟢

## Dependências

- [`hb_core`](../hb_core/): `GeoNodeCage/Cutpart/DrawerBox/Rectangle/Wall`, `hb_utils` (GN), `units`, `hb_project`. 🟢
- [`hb_placement`](../hb_placement/) e `hb_gpu_draw`: inserção e overlays. 🟢
- [`hb_layouts`](../hb_layouts/): `hb_details`. 🟢
- [`product_common`](../product_common/): `door_builder`, `door_profiles`, `types_appliances`, `wood_hoods`,
  `appliance_spec_registry`, `accessory_registry`. 🟢
- [`frameless`](../frameless/): `types_frameless.CabinetPart`, `types_products` (HalfWall, SupportFrame). 🟢
- `operators/viewport_hud`; `ui/menu_apend.py` lê `MENU_ID`. 🟢
- Assets `face_frame_assets/` (puxadores, perfis, perfis de porta) e `face_frame_thumbnails/`. 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Solver Python puro em vez de drivers | `types_face_frame.py:1-16`; `solver_face_frame.py:1-23` | 🟢 |
| Recalcular tudo a cada mudança, com coalescência por `suspend_recalc` | `types_face_frame.py:81-107` | 🟢 |
| Distribuição por travas (locked/unlocked + share) reutilizada em bays, árvores, cantos e painéis | `types_face_frame.py:1641`, `:1763`; `types_face_frame_corner.py:195`; `ops_appliance_panels.py:120` | 🟢 |
| Auto-lock na edição do usuário, distinguindo escrita de sistema | `props_hb_face_frame.py:4031-4098` | 🟢 |
| Árvore recursiva de aberturas (splits H/V) em vez de splitters fixos | `solver_face_frame.py:2993` | 🟢 |
| Frentes e itens internos apagados e recriados; carcaça reconciliada por identidade | `types_face_frame.py:5785-5975` | 🟢 |
| Exposição e acabamento automáticos com override manual por lado | `exposure.py`; `props_hb_face_frame.py:3983-4009` | 🟢 |
| Presets declarativos de bay | `bay_presets.py` | 🟢 |
| Estilo vinculado por nome, com âncoras de renomeação no `load_post` | `props_hb_face_frame.py:1690`, `:8105-8155` | 🟢 |
| Catálogo comercial embutido (CWP) gerado de planilhas | `style_options.py` | 🟢 |

## Estado Interno

- **Por objeto** (`bpy.props`): `face_frame_cabinet/bay/split/opening/interior_*`, produtos. Persistido. 🟢
- **Metadados** (ID props): tags `IS_*`, `CLASS_NAME`, `STYLE_NAME`, `hb_part_role`, índices, `SIZE_ROLE`, flags manuais. 🟢
- **Por cena**: `Scene.hb_face_frame` (padrões, estilos, preferências de acabamento). Persistido. 🟢
- **Globais de processo**: `_RECALC_SUSPEND_DEPTH`, `_PENDING_RECALC_NAMES`, `_RECALCULATING` (`id(root)`),
  `_DISTRIBUTING_WIDTHS`. Não persistidos. 🟢
- **Draw handlers**: `dim_edit_overlay` (permanente), `split_preview` (durante o diálogo). 🟢
- **Arquivo do usuário**: cores e biblioteca em `extension_path_user`. 🟢

## Observabilidade

- Sem logging estruturado. 🟢
- `report` nos operadores; falha na criação vira `CANCELLED` com mensagem (`ops_placement.py:3543`). 🟢
- Exceções engolidas no dreno de recálculo e no registro (`types_face_frame.py:103-106`; `props_hb_face_frame.py:8064-8085`). 🟢
- Solver devolve valores neutros (0.0, listas vazias) para índices inválidos — erros não aparecem. 🟢

## Riscos e Lacunas

- 🔴 Recálculo dos cantos, passes pós-recálculo, divisórias de profundidade variável e solvers de itens internos não extraídos em detalhe.
- 🔴 Produtos Leg/FloatingShelf/Valance com `recalculate` próprio não documentado.
- 🟢 Escrita `cab_props['refrigerator_opening_height']` (`types_face_frame.py:7335`) — viola a regra de `bpy.props` por atributo.
- 🟢 Enums dinâmicos sem cache das strings (`props_hb_face_frame.py:195-258`, `:6406-6425`).
- 🟢 `split_preview` sem remoção no `unregister()` (`split_preview.py:218-236`).
- 🟢 Registro que engole exceções; `bl_idname` no namespace legado `hb_face_frame.*`.
- 🟢 Helpers GN de `hb_utils` em vez de `compat.py`.
- 🟢 Classes ausentes de `WRAP_CLASS_REGISTRY` zeram o rodapé.
- 🟡 Guardas por `id(obj)`; recriação de objetos deixa malhas órfãs; muitas escritas fora de `suspend_recalc` (até ~9 recálculos por gabinete na exposição).
- 🟡 `_redistribute_split_node` grava tamanhos exibidos sem considerar overrides por membro, membros removidos, remove_bottom e front_drop.
- 🟢 Premissas americanas (moldura 3/4", carcaça 1/2", costas 1/4", base 876 mm, catálogo CWP, Blum/KV, geladeira 69") —
  decisão de mercado em `product_common` Q-06; permanência da unit em [`questions.md`](questions.md) Q-01.
- 🟢 Não alimenta a lista de corte (`cutting/`).
