# catalog_molding — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#catalog_molding`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Interface

### Molduras (`molding/`, registrado em `__init__.py:55, 245, 268`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `ops.apply_scene_packages` | `(scene)` | — | Limpa e recria tudo; aborta em cenas de layout/detalhe (`molding/ops.py:246`) 🟢 |
| `ops.clear_scene_molding` | `(scene, molding_type=None)` | — | Remove sweeps `IS_HB_MOLDING_SWEEP` e perfis marcados (`:26`) 🟢 |
| `ops._apply_type` | `(scene, molding_type, align, stack, opts)` | — | Alvos → facts → pilha → corridas → cadeias → sweeps (`:190`) 🟢 |
| `ops._spawn_sweep` | `(scene, molding_type, chain, segments, profile_ref, …)` | `Object \| None` | Curva 2D `bevel_mode='OBJECT'` (`:126`) 🟢 |
| `ops._resolve_stack` / `_base_stack` / `_sweep_z` / `_crown_datum` / `_crown_stack_top` | — | — | Pilhas e cotas (`:46-243`) 🟢 |
| `ops.on_package_changed` | `(self, context)` | — | Callback `update=` das 13 props `molding_*` (`:300`) 🟢 |
| `blendertomob.refresh_room_molding` | operador | `{'FINISHED'}` | `home_builder_OT_refresh_room_molding` (`:310`) 🟢 |
| `engine.members_touch` / `connected_components` / `order_chain` | `(…, align='top')` | — | Corridas e cadeias (`engine.py:85-152`) 🟢 |
| `engine.offset_polyline_right` / `offset_polygon_right` | `(points, offset)` | `list` | Meia-esquadria (`:159`, `:195`) 🟢 |
| `engine.corner_plan_data` | `(obj, corner_facts)` | — | Canto em L (`:231`) 🟢 |
| `engine.chain_sweep_points` | `(chain, facts, face_offset, end_offset)` | pontos | Crown/rail/cap (`:348`) 🟢 |
| `engine.kick_sweep_segments` | `(chain, facts, x_off, include_recessed)` | segmentos | Rodapé e ilhas (`:711`) 🟢 |
| `adapters.collect_targets` / `collect_bridges` / `build_facts` / `finish_material` | `(scene, …)` | — | Por biblioteca (`adapters.py:45-163`) 🟢 |
| `packages.register_profile_path` / `unregister_profile_path` / `profile_paths` | `(path)` | — | Packs externos (sem chamador) (`packages.py:35-51`) 🟢 |
| `packages.package_stack` / `enum_items` / `make_profile_object` / `profile_top_height` / `profile_front_depth` | — | — | Presets e perfis (`:136-347`) 🟢 |

### Catálogo (`catalog/`, **não registrado**)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `catalog_data.CATALOG` | `list[dict]` | — | 78 entradas (7 reais, 71 stubs) (`catalog/catalog_data.py:78-346`) 🟢 |
| `props_catalog.HBCatalogItem` / `HBCatalogState` | `Scene.hb_catalog` | — | Espelho para `UIList`; sync por timer e `load_post` (`props_catalog.py`) 🟢 |
| `previews_catalog.get_icon_id` / `reload` | — | `int` | `bpy.utils.previews` (`previews_catalog.py:29-118`) 🟢 |
| `hb_catalog.activate_item` / `hb_catalog.not_yet_implemented` | operadores | — | Despacho e fallback (`ops_catalog.py:53-108`) 🟢 |
| `render_thumbnails.render_entry` / `render_all` | `(entry)` / `()` | — | Sem chamador (`render_thumbnails.py:45-198`) 🟢 |
| `HB_UL_catalog` / `HB_CATALOG_PT_browser` | UI | — | Chama o operador inexistente `hb_catalog.render_thumbnail` (`ui_catalog.py:275-280`) 🟢 |

## Fluxo Principal

### F1. Aplicar pacotes de moldura 🟢 (fluxograma `flowcharts/legacy-catalog_molding.md`)
1. Prop `molding_*` muda → `on_package_changed` (exceções → `print`) ou operador `refresh_room_molding`.
2. `apply_scene_packages`: aborta sem `scene.home_builder` ou em `IS_LAYOUT_VIEW`/`IS_DETAIL_VIEW`.
3. `clear_scene_molding(scene)`; monta `opts` das props da sala.
4. Para cada tipo em `_TYPES` (CROWN, BASE, LIGHT_RAIL): resolve a pilha → `_apply_type`.
5. Se `molding_crown_furniture_cap`, aplica CAP.

### F2. `_apply_type` 🟢 (fluxogramas `legacy-catalog_molding-resolve_stack.md`, `-chain_sweep_points.md`, `-kick_sweep_segments.md`)
1. `collect_targets` (+ `collect_bridges` para BASE) → `build_facts`.
2. `_resolve_stack` (override por categoria, `STACK_FRONT`/`STACK_OFFSET`).
3. `connected_components` → descarta componentes só com bridges → `order_chain`.
4. Por entrada da pilha: `kick_sweep_segments` (BASE) ou `chain_sweep_points` (demais) → `_spawn_sweep`.

### F3. `_spawn_sweep` 🟢
Perfil (pack ou contorno embutido) → curva 2D `bevel_mode='OBJECT'`, `use_fill_caps`, tags `IS_HB_MOLDING_SWEEP`,
`HB_MOLDING_TYPE`, `HB_MOLDING_MEMBERS` → parent no 1º membro → `location.z = _sweep_z(...)` → pontos no espaço local
(dedup 1e-4), uma spline BEZIER com handles VECTOR por segmento → material do 1º membro que resolver. Sem splines →
remove os objetos (não as curvas).

### F4. Catálogo (se reativado) 🟢 (fluxograma `legacy-catalog_molding-activate_item.md`)
`register` cria previews → props + `load_post` + sync adiado → operadores → UI. `activate_item`: `find_entry` → resolve
`bpy.ops.<mod>.<op>` → chama com `action_args` → `_apply_global_assembly_config(context.active_object)`; `AttributeError`
→ `draw_cabinet('INVOKE_DEFAULT', cabinet_name='Base Door')`.

## Fluxos Alternativos

- **Cena de layout/detalhe ativa:** nada é feito. 🟢
- **Componente só com bridges:** descartado. 🟢
- **Sem pack de perfis:** contorno embutido; sem contorno → sem sweep. 🟢
- **Sweep sem splines:** objetos removidos, curva órfã. 🟢
- **Exceção no callback de pacote:** só `print`. 🟢
- **Gabinete alterado depois:** molduras ficam como estão até o refresh. 🟢
- **Catálogo — `getattr` de operador inexistente:** fallback para `draw_cabinet` Base Door. 🟡
- **Catálogo — estilo aplicado ao objeto ativo** logo após abrir um modal: provável objeto errado. 🟡
- **Catálogo — render em `--background`:** `context.window` é `None` → falha. 🟡

## Dependências

- [`hb_core`](../hb_core/): `hb_props.Home_Builder_Scene_Props.molding_*` (13 props com `update`), `hb_types.GeoNodeObject.get_input`,
  `hb_project.get_main_scene`, `units.inch`. 🟢
- [`face_frame`](../face_frame/): `find_cabinet_root`, `ensure_default_styles`, `get_style_props`, `draw_molding_ui`
  (UI das molduras e botão de refresh), `hb_face_frame.draw_cabinet`. 🟢
- [`frameless`](../frameless/): `props_hb_frameless` (estilos para material e config global). 🟢
- Marcadores: `IS_FACE_FRAME_CABINET_CAGE`, `IS_FRAMELESS_CABINET_CAGE/PRODUCT_CAGE`, `IS_CORNER_CABINET`, `IS_APPLIANCE`,
  `IS_WALL_BP`, `IS_FACE_FRAME_BAY_CAGE`, `hb_part_role=='TOP_RAIL'`, `CLASS_NAME=='RefrigeratorCabinet'`, `IS_LAYOUT_VIEW`,
  `IS_DETAIL_VIEW`. 🟢
- **Sobreposição funcional** com `frameless/operators/ops_crown.py`, `ops_toe_kick.py`, `ops_upper_bottom.py` (molduras por
  perfil desenhado em cena de detalhe) e com `closets/molding_closets.py`. 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Molduras por pacote da sala, reconstruídas por inteiro (idempotente) | `molding/ops.py:246-297` | 🟢 |
| Geometria agnóstica (`engine`) separada dos adaptadores por biblioteca | `molding/engine.py`; `molding/adapters.py` | 🟢 |
| Sweep por curva 2D com `bevel_object` (perfil) | `molding/ops.py:126-187` | 🟢 |
| Perfis por pack externo plugável com fallback embutido | `molding/packages.py:35-252` | 🟢 |
| Catálogo como lista Python estática com stubs | `catalog/catalog_data.py` | 🟢 |
| Enums de pacote cacheados no módulo (evita GC) | `molding/packages.py:55-58` | 🟢 |

## Estado Interno

- **Por cena**: 13 props `Scene.home_builder.molding_*` (pacotes, overrides, reveal, offsets, toggles). Persistido. 🟢
- **Objetos gerados**: sweeps (`IS_HB_MOLDING_SWEEP`, `HB_MOLDING_TYPE`, `HB_MOLDING_MEMBERS` = nomes separados por vírgula)
  e perfis (`IS_HB_MOLDING_PROFILE`). Persistidos; recriados a cada aplicação. 🟢
- **Cache de módulo**: métricas de perfil e itens de enum; packs registrados. 🟢
- **Catálogo**: `Scene.hb_catalog`, coleção de previews, flag `_sync_pending` e timer. 🟢

## Observabilidade

- `print` em falhas do callback de pacote (`molding/ops.py:300-307`). 🟢
- `report` + `CANCELLED` no `activate_item` do catálogo. 🟢
- `render_all` acumula `(rendered, skipped, errors)`, mas não tem chamador. 🟢

## Riscos e Lacunas

- 🔴 `catalog/` não registrado; operador `hb_catalog.render_thumbnail` inexistente (o painel quebraria ao selecionar um item).
- 🔴 Sem adaptador de molduras para closets; três implementações de moldura no projeto.
- 🔴 Nenhum pack de perfis no repositório.
- 🟢 Reconstrução pesada dentro de `update=` (objetos, `libraries.load`, remoção de datablocks); `register()` que engole exceções.
- 🟢 Curvas órfãs em sweeps vazios; materiais auxiliares de packs não limpos 🟡.
- 🟢 Catálogo: timer não cancelado no `unregister`, enum sem cache, miniaturas na pasta do add-on, `studio_light='basic_grey.exr'`
  dependente da instalação 🟡, render dependente de `context.window`.
- 🟡 `HB_MOLDING_MEMBERS` por nomes separados por vírgula quebra se um nome tiver vírgula.
- 🟢 Medidas dos contornos embutidos e defaults em polegadas (reveal 0,625", stack offset 3,5").
