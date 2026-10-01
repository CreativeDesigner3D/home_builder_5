# Investigation: Add-on de Móveis Planejados — incremento 1

> Feature `001-addon-moveis-planejados` · Data `2026-10-01`

## 1. Fontes consultadas

| Fonte | O que trouxe |
|---|---|
| `promob_pacote_completo.zip:documentos/analise_requisitos_promob*.md` (v1–v4) | RF01–RF115, RN01–RN54, RNF01–RNF51 observados em 6 vídeos do Promob Plus Enterprise |
| `promob_pacote_completo.zip:documentos/casos_uso_criterios_configuracao_dimensoes_promob.md` | UC-DIM-01..13, CA-DIM-001..049; registro mínimo de parâmetro |
| `promob_pacote_completo.zip:configuracoes/PROMOBCONFIGURAÇÃOMEDIDASMEMOVEIS.xml` | Formato `DIMENSIONEXPORT`; distribuição de valores (15 mm ×174, `MDF` ×121, 2730/1810 ×107) |
| `evidencias/issue20-configurador-dimensoes.png` | Estrutura da tela: `Medidas Máximas`; linha → `Dimensões Externas`, `Chapas` (17), `Componentes`; campos A–H por chapa |
| Issue `CreativeDesigner3D/home_builder_5#20` | 7 pedidos (Blender 5.2, unidades, pt-BR, dimensões com imagem, plano de corte, JSON global, limite MDF) |
| `docs/rag/promob/corpus/06-projeto-ii.md#6-1-2-como-definir-dimensoes-padroes` | Itens A–L das dimensões externas |
| `docs/rag/promob/corpus/19-configuracao-de-produto.md` | Chapas por peça e integração com o Promob Cut |
| `docs/rag/promob/corpus/22-edicoes.md#22-2-modulos`, `23-plano-de-corte.md` | Lista de peças, indicações de peça incompatível, plano de corte, ID único |
| `_reversa_sdd/hb_core/node-group-interfaces.md#geonodecutpart` | `Length`, `Width`, `Thickness`, `Edge W1/W2/L1/L2` (Blender 5.2.0) |
| `_reversa_sdd/cutting/design.md`, `adrs/0002-nested-cutlist-algorithm.md` | Nesting atual e por que é guilhotinado |
| `docs/rag/blender-api/corpus/bpy.utils.md`, `bpy.utils.previews.md`, `bpy.types.UILayout.md`, `bpy.types.WindowManager.md` | APIs da interface do Configurador |

## 2. Alternativas avaliadas

### 2.1 Como os módulos seguem o padrão (D-05)

| Alternativa | Prós | Contras | Decisão |
|---|---|---|---|
| A. Sincronizar o padrão nas props de cena das bibliotecas legadas + atualizar gabinetes existentes | Sem reescrever frameless/closets; entrega RN-23 no incremento 1 | Duas fontes (padrão e props legadas) até a migração; precisa de relatório de cobertura | **Escolhida** para o incremento 1 |
| B. Bibliotecas leem o padrão diretamente | Uma fonte de verdade | Toca milhares de linhas; alto risco no primeiro incremento | Alvo do incremento 3 |
| C. Drivers apontando para o padrão | Propagação automática | Drivers frágeis entre versões (`hb_core` Q-02), lentos em cenas grandes | Descartada |

### 2.2 Fonte da lista de peças (D-08)

| Alternativa | Prós | Contras | Decisão |
|---|---|---|---|
| A. Inputs do `GeoNodeCutpart` | Dimensões de corte e fitas por aresta; semântica por peça | Depende da avaliação do depsgraph e da tabela de papéis | **Escolhida** |
| B. Malha avaliada (`obj.evaluated_get().to_mesh()`) | Geometria exata | Perde componente, fita e veio; entalhes viram polígonos | Descartada (usar só para validação) |
| C. Síntese a partir das dimensões externas (atual) | Simples | Errada para qualquer gabinete real (lacuna L1) | Fallback |

### 2.3 Algoritmo de corte (D-13)

Next-Fit Decreasing guilhotinado (atual) × maxrects × skyline × solver MIP. Mantido o atual: compatível com seccionadoras
guilhotinadas, determinístico, stdlib. Melhorias de aproveitamento ficam para depois do incremento 1, com o JSON v2
permitindo usar otimizadores externos.

### 2.4 Validação do JSON (D-14)

Biblioteca de JSON Schema externa × validador mínimo próprio. As extensões do Blender não devem depender de pacotes fora
da stdlib (`_reversa_sdd/dependencies.md`); o validador próprio cobre campos obrigatórios, tipos, unidades e referências
cruzadas. O esquema é publicado como documento (`interfaces/json-global-v2.md`) para validação por terceiros.

### 2.5 Onde guardar o padrão (D-03)

Cena principal (viaja com o `.blend`) + arquivos do usuário (distribuição). Só arquivos perderia o histórico do projeto;
só cena impediria padronizar a empresa.

### 2.6 Interface do Configurador (D-16, D-17)

Diálogo `invoke_props_dialog` com árvore em `template_list` e imagem por `template_icon` (coleção `bpy.utils.previews`)
atende à tela do Promob dentro dos limites da UI do Blender. Janela própria por GPU foi descartada (custo e acessibilidade).

## 3. Padrões aplicáveis

- **Rascunho + aplicar atômico** (transação de UI): edita-se uma cópia; aplicar é um operador com `UNDO` (RN-22).
- **Esquema declarativo de parâmetros** (metadados em código, valores em dado): domínios revisados no código, valores do usuário.
- **Adaptador por fonte** para peças (frameless, closets, geometria livre, `btm_*`), com classificação por tabela.
- **Identificador estável** em vez de nome de objeto para tudo que sai do projeto.
- **Preservação do desconhecido** em importação de formatos de terceiros (`raw_attributes`).

## 4. Questões técnicas em aberto (não bloqueiam)

- Lado ↔ aresta (`Edge W1/W2/L1/L2` ↔ fita 1..4) precisa de conferência com 3 gabinetes de referência.
- Peças com modificadores `CPM_*` (entalhes, chanfros, recortes): a dimensão de corte é a do retângulo envolvente; a
  usinagem fica para o incremento 4.
- Medir o tempo de aplicar uma definição numa cozinha de 60 módulos para validar a meta de desempenho.


---

# Incremento 3 — bloco 1: Inspeção e movimento

## I3-1. Fontes consultadas

- Survey do código atual (2026-10-01):
  - face frame: `product_libraries/face_frame/operators/op_open_mode.py`, `solver_face_frame.py` (`front_leaves`,
    `_single_door_leaf_pivot`, `_drawer_or_pullout_slide_leaf`, `DOOR_MAX_SWING_ANGLE`), `props_hb_face_frame.py`
    (`swing_percent`, `hinge_side`);
  - closets: `op_open_door_closet.py`, `types_closets.py` (`apply_door_open`, `apply_drawer_open`, `DOOR_OPEN_ANGLE`);
  - frameless: `types_frameless.py` (`Doors`, `FlipUpDoor`, `Drawer`, `Pullout`, `CabinetDoor`, `CabinetFlipUpDoor`,
    `CabinetDrawerFront`, `CabinetPulloutFront`);
  - camada moderna: `geometry/door_controller.py`;
  - posicionamento: `hb_placement.py` (`PlacementMixin.find_placement_gap` e intrusões), `operators/viewport_hud.py`
    (`_ModalToggleButton`, registro de modais).
- RAG Blender 5.2:
  - `docs/rag/blender-api/corpus/bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.setup`
  - `docs/rag/blender-api/corpus/bpy.types.Gizmos.md#bpy.types.Gizmos.new`
  - `docs/rag/blender-api/corpus/bpy.types.Gizmo.md#bpy.types.Gizmo.target_set_handler`
  - `docs/rag/blender-api/corpus/bpy.app.handlers.md#bpy.app.handlers.save_pre` / `#bpy.app.handlers.save_post`
  - `docs/rag/blender-api/corpus/mathutils.bvhtree.md#mathutils.bvhtree.BVHTree.FromObject` / `#mathutils.bvhtree.BVHTree.overlap`
- Promob: RF09/RF78 (abrir portas), RF10/RF107 (colisão), RN38/RN48/RN51 (`requirements.md` RN-14); manual §3.8
  "Colisão" (`docs/rag/promob/`).

## I3-2. Alternativas avaliadas

### Como abrir as frentes do frameless
| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| `delta_rotation_euler`/`delta_location` na própria peça | Sem objetos novos; não conflita com drivers de medida; reversível zerando | Basculante precisa de compensação de pivô | **Escolhida (D-21)** |
| Empty pivô por porta (como o face frame) | Rotação trivial | Muda a hierarquia e o recálculo de todos os gabinetes; arquivos antigos | Descartada |
| Driver em `rotation_euler` lendo um prompt | Persistente no arquivo | Conflita com rotação estática; drivers frágeis (Q-02) | Descartada |
| Input de Geometry Nodes (`GeometryNodeGizmoDial`) | Gizmo nativo de GN | A porta é objeto, não geometria do nó; exigiria refazer as frentes em GN | Descartada |

### Controle no 3D
| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| `GizmoGroup` com `GIZMO_GT_dial_3d` / `GIZMO_GT_arrow_3d` | Nativo, arrastável, com encaixe controlável no `set` | Sem exemplo no repositório; pólo precisa ser barato | **Escolhida (D-25)** |
| Empty controlador com restrição (padrão `btm` atual) | Já existe | Um por módulo, linear, sem paradas, polui o outliner | Descartada |
| Modal próprio com desenho em `POST_VIEW` | Total controle | Reimplementa o que o gizmo oferece | Descartada |

### Interferência
| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Envelope varrido + AABB + `BVHTree.overlap` | Preciso o bastante; rápido com pré-filtro | Amostragem angular | **Escolhida (D-29)** |
| Só AABB | Muito rápido | Falso positivo em L, paredes e cantos | Descartada |
| Booleana de interseção | Exata | Lenta; cria dados; frágil | Descartada |

### Salvar fechado
| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| `save_pre` fecha / `save_post` reabre | Arquivo em disco fechado; vista preservada | Custo no salvamento | **Escolhida (D-28)** |
| Fechar no `load_post` | Simples | Arquivo em disco continua aberto | Descartada |

## I3-3. Padrões aplicáveis

- Adaptador por linha de produto, como `cutting/part_sources.py` no incremento 1.
- Animação por timer de modal + *smoothstep*, igual aos modos legados (`op_open_mode.py`, `op_open_door_closet.py`).
- Contrato de modal do HUD (`register_active_modal`, `_exit_requested`, `click_hits_widget`).
- Matemática de pivô (rotacionar em torno de uma aresta): `delta_location = R·(o − h) + h − o`, com `o` a origem e `h`
  um ponto da aresta da dobradiça, ambos no espaço do pai; testável em Python puro com `mathutils`.

## I3-4. Questões técnicas em aberto (não bloqueiam)

- Portas de canto do frameless (`add_corner_doors`): as duas folhas articulam no entalhe; verificar o sinal e o eixo
  no teste antes de expor no gizmo.
- `TILT_OUT` do face frame não é clicável hoje (`OPENING_FRONT_ROLES`); entra no adaptador como `FLIP_DOWN`.
- Possível tipo de dobradiça (45°/90°/110°/165°) como dado de catálogo — ver premissa do roadmap.
