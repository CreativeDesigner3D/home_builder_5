# Impacto no legado — 002-editor-parede-mover-sobre

> Gerado por `/reversa-coding` em 2026-10-05.
> - Rodada 1: blocos B1 (propriedades e cotas) e B2 ("Mover Sobre") — T001, T002, T004–T006, T009, T011–T015, T017, T018, T023–T027.
> - Rodada 2: B3 (Editor de Paredes), B4 (geometria e operações de parede), T036 e o fechamento — T003, T007, T008, T010, T019–T022, T028–T040.
> - Fechamento e pé-direito: T074–T090 — ímã e pergunta de fechamento (editor e "Desenhar Paredes" 3D), rede de segurança no OK, pé-direito do projeto.
> - Revisão pós-auditoria ao vivo: T054–T073 — Direção e medida real interna, digitação direta, botão direito em todos os modos, OK/Cancelar, gizmo, desregistro completo.
> - Revisão (pós-auditoria e esclarecimentos): T041–T053 e T016 — folha 3D das portas de ambiente, pergunta dos módulos no OK, conversão de paredes da camada nova.

## Tabela de impacto

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `blendertomob/selection/classify.py`, `selection/editing.py` | seleção (novo) | componente-novo | MEDIUM | Classificador único de tipo (RN-01) e leitura/escrita de dimensões por biblioteca |
| `blendertomob/measure/cotas.py`, `measure/scene_cotas.py` | cotas (novo) | componente-novo | MEDIUM | Cotas de RN-04 calculadas e editáveis. Lê os filhos da parede pelo `PlacementMixin` sem alterá-lo. `slide` para no vizinho ao arrastar |
| `blendertomob/canvas2d/view.py`, `canvas2d/draw.py` | telas 2D (novo) | componente-novo | LOW | Transformação, grade, encaixe e desenho 2D |
| `blendertomob/move_over/*` | "Mover Sobre" (novo) | componente-novo | HIGH | Atalho de add-on no botão direito do "3D View" (só age com o modo ligado), arraste, janela de alinhamento e "Mover na Parede" |
| `blendertomob/walls2d/*` | editor de paredes 2D (novo) | componente-novo | HIGH | Lê as cadeias de paredes do HB5 e, no OK, cria, atualiza e remove paredes (mesmo `GeoNodeWall.create`/`connect_to_wall` do construtor) e recalcula as esquadrias. Abre uma janela nova (Image Editor) |
| `blendertomob/inspection/room_door_math.py`, `inspection/room_door_leaf.py`, `inspection/adapters/room_doors.py` | inspeção (001) + portas de ambiente | regra-nova | MEDIUM | Portas `IS_ENTRY_DOOR_BP` com símbolo de abertura ganham, no primeiro "Abrir", pivô e folha 3D filhos (sem mexer no node group); entram em `inspection.fronts` e no salvar fechado |
| `blendertomob/inspection/fronts.py`, `inspection/interference.py` | inspeção (001) | regra-alterada | LOW | `module_root_of` reconhece a porta de ambiente; `Front.can_sweep()` impede a verificação de interferência de criar folhas |
| 46 arquivos legados com `register()`/`unregister()` (operadores, menus, propriedades e painéis de `operators/`, `product_libraries/*`, `data/properties.py`, `hb_props*.py`, `hb_project.py`, `hb_assets.py`, `molding/ops.py`) | núcleo de registro (todas as bibliotecas) | regra-alterada | HIGH | O desregistro usa a própria classe (`cls.is_registered`); antes 280 operadores ficavam registrados após desligar a extensão |
| `blendertomob/operators/walls.py` (`home_builder_walls_OT_draw_walls`) | construtor 3D de paredes (legado) | regra-alterada | HIGH | "Close snap" de 0,15 m que fechava sem perguntar → ímã de 15 px de tela e pergunta antes do `close_room`; medida digitada que termina no início também pergunta; tecla C inalterada |
| `blendertomob/hb_props.py` (`update_ceiling_height`) | propriedades do projeto (legado) | regra-alterada | MEDIUM | Além dos armários, atualiza `Height`/`End Height` das paredes de altura cheia (fora Mureta, `Half`, `Fake`) |
| `blendertomob/walls2d/heights.py`, `walls2d/apply.py` (`height_mismatches`, `sync_project_height`, fechamento no OK) | editor de paredes 2D | regra-nova | MEDIUM | Pé-direito do projeto e rede de segurança do fechamento |
| `blendertomob/move_over/ops_drag.py` | "Mover Sobre" | regra-alterada | MEDIUM | Atalho do botão direito também nos 19 mapas de modo da viewport (antes o menu de contexto do Modo Objeto capturava o clique) |
| `blendertomob/inspection/gizmo.py` | inspeção (001) | regra-alterada | LOW | A seta das gavetas não consulta `travel()` de portas (erro a cada redesenho com porta selecionada) |
| `blendertomob/walls2d/convert.py` | editor de paredes 2D | componente-novo | MEDIUM | Paredes da camada nova (`btm_wall_segments`) convertidas, sob pergunta, em paredes do HB5 no OK; o objeto original é removido |
| `blendertomob/geometry_free/*` | geometria livre (novo) | componente-novo | MEDIUM | Placa e caixa com `btm_plane.object_kind = 'GEOMETRY'` e `Object.btm_geometry` |
| `blendertomob/cutting/part_sources.py`, `cutting/part_extractor.py` | cutting (extração de peças) | regra-nova | MEDIUM | Nova origem `FREE_GEOMETRY`: geometria marcada como peça de fabricação entra na lista de peças, no plano de corte e no JSON v2 (sem módulo) |
| `blendertomob/operators/ops_wall_extras.py`, `operators/__init__.py` | operators (paredes) | componente-novo | MEDIUM | Remover parede com opções, rebaixar e invisível. `remove_wall` também serve ao editor. `home_builder_walls.delete_wall` não foi alterado |
| `blendertomob/ui/menus.py` | ui (menu da parede) | regra-alterada | LOW | `HOME_BUILDER_MT_wall_commands` ganha "Editar Paredes…", "Rebaixar Parede", "Visibilidade" e "Remover Parede…"; os itens antigos continuam |
| `blendertomob/ui/object_properties.py`, `ui/panels.py`, `ui/__init__.py` | ui (painéis) | regra-alterada | MEDIUM | `BTM_PT_ObjectProperties` substitui `BTM_PT_ContextProperties` e mostra os grupos Geometria, Parede (com operações) e "Mover na Parede". O Construtor ganha "Editor de Paredes", "Placa" e "Caixa" |
| `blendertomob/ui/panels.py` (Gerenciador de Ambientes) | ui (painéis) | regra-alterada | MEDIUM | Correção A002: botões de ambiente chamavam `home_builder.*_room` inexistentes; agora `blendertomob.*_room` (operadores de `operators/rooms.py`) |
| `blendertomob/overlays/selection_cotas.py`, `overlays/__init__.py` | overlays | componente-novo | LOW | Cotas desenhadas ao selecionar um módulo |
| `blendertomob/operators/viewport_hud.py` | HUD | regra-alterada | LOW | Botão "Mover Sobre" |
| `blendertomob/data/i18n.py` | data (traduções) | regra-alterada | LOW | Strings novas pt-BR → en |
| `blendertomob/__init__.py` | núcleo do add-on | regra-alterada | LOW | Registro de `move_over`, `walls2d` e `geometry_free` (com hot-reload), com `unregister()` simétrico |
| `docs/usuario/editor-paredes-e-mover-sobre.md` | documentação | componente-novo | LOW | Guia do usuário |
| `tests/*` | testes | componente-novo | LOW | Testes de `canvas2d`, alinhamento, cotas (com deslizar), classificador e modelo de paredes, mais a fumaça `blender_002_smoke.py` |

## Diff conceitual por componente

**ui.**
- O painel de propriedades deixa de reconhecer só a camada nova (`btm_plane`). Agora mostra, para o objeto ativo de qualquer biblioteca, os grupos do tipo dele e uma linha de estado:
  - Dimensões, Cotas, Abrir, Ações (gabinetes);
  - Parede, com editor, rebaixar, visibilidade e remover;
  - Geometria, com medidas, fabricação, duplicar, espelhar e excluir;
  - Outras.
- A edição passa por propriedades virtuais da cena, então cada edição é um passo de desfazer.
- As portas de ambiente mostram que não têm folha 3D.

**"Mover Sobre".**
- Novo modo: com ele ligado, o botão direito na viewport inicia um arraste entre dois objetos e abre uma janela de alinhamento. Desligado, o botão direito continua com o menu de contexto do Blender.
- "Mover na Parede" arrasta o módulo só no plano da parede e para no vizinho quando "Evitar Sobreposição" está ligado.

**cotas.** As cotas anterior, posterior, inferior, superior e afastamento passam a existir para módulos de parede. O cálculo usa os mesmos filhos e o mesmo filtro vertical do posicionamento, e as cotas são editáveis.

**Editor de paredes.**
- Desenha e edita as paredes do HB5 numa planta 2D, sobre um rascunho em memória.
- No OK, segue o caminho do construtor (`hb_core` RN-15: cadeia por `COPY_LOCATION` no `obj_x`) e recalcula as esquadrias com `update_all_wall_miters`.
- Paredes removidas no editor saem pela mesma rotina do "Remover Parede…", que:
  - solta a vizinha da direita na posição atual;
  - limpa `connected_object` da esquerda;
  - deixa os módulos soltos.
- Tipo e orientação ficam nas idprops `btm_wall_type` e `btm_wall_orientation`. Sem elas, a leitura assume Normal/Direita (M-07).
- No OK, pisos e tetos existentes têm a malha refeita com o contorno novo (mesmas funções de `add_floor`/`add_ceiling`, correção A005). Paredes da camada nova aparecem como referência tracejada (D-05, correção A004).

**Portas de ambiente.** Antes só recorte e símbolo 2D. Agora:
- o primeiro "Abrir" cria um pivô na dobradiça e a folha 3D;
- lado e sentido seguem o símbolo (`Is Left`, `Is Double`, `Swing Inside`);
- a porta passa pela inspeção da 001: abrir/fechar, controle giratório e salvar fechado com `btm_open`.

Portas nunca abertas não mudam. O node group do Home Builder 5 não foi alterado.

**Editor de paredes (revisão).**
- No OK, os módulos de trechos apagados são listados com a caixa "Remover os módulos junto?" (padrão: ficam soltos).
- Paredes da camada nova selecionadas podem ser convertidas em paredes do HB5 (orientação Centro, base no piso).
- A esquadria do deslocamento de orientação nos cantos foi corrigida.

**Editor de paredes (pós-auditoria ao vivo).** Os nós passam a ser a face interna (medida real) e cada cadeia tem
uma Direção (lado da espessura); salas fechadas ficam com a espessura para fora e o interior em −Y local, como o Home
Builder espera para módulos e portas. Digitação direta na face ou no vértice; face interna tracejada; OK/Cancelar no
fim do painel com confirmação; a região lateral abre na aba do editor e sem o cabeçalho do Image Editor.

**Fechamento e pé-direito.** O editor e o construtor 3D passam a ter ímã de 15 px no ponto inicial e a perguntar
antes de fechar (clique, teclado ou arraste); o OK do editor fecha qualquer contorno com o fim no início. As paredes
novas do editor nascem com o pé-direito do projeto, o OK oferece igualar as existentes e mudar o pé-direito nas
Configurações atualiza todas as paredes de altura cheia.

**Registro.** Todos os `unregister()` legados passaram a remover a própria classe registrada. Desligar ou atualizar a
extensão não deixa mais operadores, menus ou painéis antigos ativos.

**Operações de parede.**
- **Remover:** Segmento, Tudo ou Manter o selecionado, com ou sem os módulos.
- **Rebaixar:** a parede fica com `hide_viewport` e aparece uma filha de 150 mm; os dados de altura não mudam.
- **Invisível:** `display_type = 'WIRE'`, com a opção de esconder o contorno. Vale também para o teto.

**cutting.** A extração de produção ganha o adaptador `FREE_GEOMETRY`:
- **Placa:** 1 chapa. Comprimento e largura são as duas maiores medidas; a espessura é a menor.
- **Caixa:** 6 chapas.
- O `module_uid` fica nulo e a matéria-prima digitada é mantida. As regras de nesting (refilo, kerf, fibra, guilhotina) não mudam.

## Preservadas

- `_reversa_sdd/domain.md` R-01 a R-10: código não tocado.
  - R-03 (sentido da parede no construtor) continua no construtor; o editor tem a sua própria orientação, só para paredes novas.
- `_reversa_sdd/hb_core/requirements.md` RN-15 (encadeamento por `COPY_LOCATION` no `obj_x`): o editor usa `connect_to_wall`. RN-29 (hierarquia por marcadores, incluindo `IS_WALL_BP`): as paredes criadas pelo editor têm o marcador do `GeoNodeWall.create`.
- `_reversa_sdd/hb_placement/requirements.md` RN-09 a RN-14: só leitura (`get_wall_children_sorted`, `avoid_overlap`), sem mudança.
- `_reversa_sdd/cutting/requirements.md` R-01 a R-04 (refilo, kerf, fibra, guilhotina): inalteradas. As peças `FREE_GEOMETRY` passam pelo mesmo nesting.
- `_reversa_sdd/wall_editor/requirements.md` R-01 a R-05 (aberturas na parede): inalteradas.
- `_reversa_sdd/ui/requirements.md` R-01 (painéis de piso/aberturas só com paredes): inalterada.

## Modificadas

- `_reversa_sdd/ui/requirements.md#R-02` dizia: "o painel de contexto adapta-se ao tipo do objeto ativo (WALL/CABINET/OPENING)", só para a camada nova.
  - **Alterada:** um painel por tipo, para todas as bibliotecas, com cotas editáveis (rodada 1), mais geometria e operações de parede (rodada 2).
- `_reversa_sdd/soul.md` (lista de peças e plano de corte 🟢, a partir dos módulos).
  - **Ampliada:** geometria livre marcada como peça de fabricação também entra na lista de peças, no plano de corte e no JSON (`source = "FREE_GEOMETRY"`, sem módulo).
