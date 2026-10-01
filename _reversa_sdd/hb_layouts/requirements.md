# hb_layouts — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-hb_layouts`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#hb_layouts`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-hb_layouts*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Visão Geral

O `hb_layouts` produz a **documentação 2D do projeto** dentro do Blender. Cada prancha é uma **cena dedicada**
(`IS_LAYOUT_VIEW`) que instancia os objetos do cômodo por *collection instances* (sem copiá-los), fotografada por uma
câmera ortográfica travada e renderizada em Workbench com traço **Freestyle** ou **Grease Pencil Line Art**. 🟢
A unit cobre elevações de parede com cotas automáticas, planta baixa, vista 3D, multivistas de um objeto, carimbo
(title block), detalhes 2D estilo CAD com biblioteca persistente do usuário e o registro das bibliotecas de assets. 🟢

## Responsabilidades

- Criar cenas de prancha com unidades, snap e render configurados, e papel (tamanho, orientação, DPI). 🟢
- Rotear os objetos para três collections (Solid, Dashed, Ignore) e desenhar o traço por Freestyle ou Line Art. 🟢
- Criar elevação de parede com câmera ortográfica, enquadramento automático e cotas de gabinetes. 🟢
- Criar planta baixa, vista 3D e multivistas (cruz de projeções ou prancha iso + planta + elevação). 🟢
- Criar o carimbo (title block) com campos de texto. 🟢
- Assar (bake) e desassar o Line Art para edição manual. 🟢
- Criar cenas de detalhe 2D com primitivas (linha, polilinha, círculo, texto). 🟢
- Salvar, listar, carregar e excluir detalhes numa biblioteca do usuário (`.blend` + índice JSON). 🟢
- Registrar a biblioteca de assets embutida e as do usuário nas preferências do Blender, com catálogos e asset shelf. 🟢

## Regras de Negócio

IDs `HB_LAYOUTS-Rnn` de `code-analysis-legacy.md`.

**Papel e render**
- RN-01 (R01): resolução = `int(polegadas × DPI)` (trunca; padrão 150 DPI); paisagem troca largura/altura; tamanho desconhecido → LETTER; `resolution_percentage = 100`. 🟢
- RN-02 (R02): papéis (pol., retrato) — LETTER 8.5×11, LEGAL 8.5×14, TABLOID 11×17, A4 8.27×11.69, A3 11.69×16.54. Tabela duplicada em `operators/layouts.py:90`. 🟢
- RN-03 (R03): papel persiste como IDProperties da cena `PAPER_SIZE`, `PAPER_LANDSCAPE`, `PAPER_DPI` (padrões LETTER/True/150). 🟢
- RN-04 (R04): padrões inconsistentes — vistas LETTER, MultiView TABLOID, `Scene.hb_paper_size` TABLOID, preferência `default_paper_size` LEGAL. 🟢
- RN-05 (R09): render de prancha — Workbench, AA 32, cor por OBJECT, luz FLAT, SOLID. 🟢
- RN-06 (R18): câmeras de página são ORTHO, com localização/rotação travadas, `hide_select`, e viram `scene.camera`. 🟢

**Traço**
- RN-07 (R05): a engine de linha de vistas novas vem da preferência `line_engine` (padrão FREESTYLE); cada cena é carimbada com `HB_LINE_ENGINE`; sem carimbo = FREESTYLE. 🟢
- RN-08 (R06): a vista 3D sempre usa Freestyle. 🟢
- RN-09 (R07): cada cena tem `<cena>_Freestyle_Ignore` (anotações, cotas, carimbo), `<cena>_Freestyle_Dashed` (peças internas) e `<cena>_Freestyle_Solid` (geometria), com tags `IS_FREESTYLE_*`. 🟢
- RN-10 (R08): Freestyle — lineset Solid (silhueta, borda, crease, edge mark; INCLUSIVE; preto; 1,5) e Dashed (idem + HIDDEN; 1,0; traço 10 / intervalo 5). 🟢
- RN-11 (R10): Line Art — Solid oclusão 0; Dashed oclusão 1..128; tracejado por SIMPLIFY SAMPLE + DASH 3/2; IGNORE com `lineart_usage='EXCLUDE'`; GP preto, `show_in_front`, não selecionável. 🟢
- RN-12 (R11): espessuras Line Art em papel (sólida 0,010", tracejada 0,0067", passo 0,025") convertidas por `paper_to_world(valor, escala)` × fatores da cena; escala de fallback `1/4"=1'`; raio = largura. 🟢
- RN-13 (R12): câmera "jitter" para Line Art — inclinada 0,05° em pitch/yaw, compartilha o datablock, filha da câmera da cena, recriada se a câmera mudar, oculta. 🟢
- RN-14 (R13): canal Marked — peças MESH com `Rail`, `Stile`, `Door (`, `Blind Panel`, `Drawer Front` no nome são retraçadas (oclusão 0..2) em cópias ` LAEmit` elevadas 1 mm; células iso excluídas. 🟢 (sem chamador 🔴)
- RN-15 (R14): holdout de texto — retângulo vira stroke de 2 pontos (raio = meia-altura), camada `Holdout` de opacidade 0 usada como máscara invertida. 🟢 (sem chamador 🔴)
- RN-16 (R15): bake congela strokes, desliga todos os modificadores e marca `HB_LINEART_BAKED`; vistas baked não religam modificadores; unbake limpa e religa. 🟢
- RN-17 (R16): vista híbrida — células iso em `<cena>_Iso_Solid/_Iso_Dashed` desenhadas por Freestyle; sem células iso, `view_layer.use_freestyle=False`. 🟢 (sem chamador 🔴)

**Seleção de conteúdo**
- RN-18 (R17): excluídos das vistas — cages (`IS_GEONODE_CAGE`, `IS_FACE_FRAME_SPLIT_NODE`) e helpers (`obj_x`, nome com `Overlay Prompt Obj`); filhos de cages continuam percorridos. 🟢
- RN-19 (R22): conteúdo da elevação — collection da parede; por gabinete (FRAMELESS, FACE_FRAME, CLOSET_STARTER) collections Solid/Dashed com peças `IS_*_INTERIOR_PART` em Dashed; Dashed vazia removida. 🟢
- RN-20 (R29): bbox recursivo (local da origem, depsgraph avaliado) ignora anotações, cages, helpers e EMPTYs; sem geometria → `(0, dimensions)` ou `(0, (1,1,1))`. 🟢
- RN-21 (R30): dimensões do objeto da multivista = `Dim X/Y/Z` do cage; fallback `obj.dimensions`, depois (1,1,1). 🟢

**Elevação**
- RN-22 (R19): enquadramento — bbox local da parede `[0,L]×[0,H]` ∪ bound_box de filhos MESH ∪ cotas (±0,1 m X, ±0,25 m Z); margem 10% do maior lado; câmera a 3 m à frente; `ortho_scale = max(w, h)`. 🟢
- RN-23 (R20): `ElevationView.update` usa outra regra — câmera no centro a y=−2, `ortho = max(L, H) + 0,4 m`, sem cotas/filhos. 🟢
- RN-24 (R21): cotas automáticas — só filhos diretos da parede com cage FRAMELESS/FACE_FRAME; Z local > 1,2 m ⇒ superior; base/altos em z = −4" (leader −4"); superiores em topo máx. + 4" (leader +4"); 2" à frente da parede; comprimento = `Dim X`; nome `Dim_<cage>`. 🟢

**Planta, 3D e multivista**
- RN-25 (R23): planta — paredes `IS_WALL_BP` da cena de origem (ou do arquivo); bbox só pelos pontos inicial/final; câmera a z=5; `ortho = max(w, h) + 1 m`; sem paredes → (0,0,5), ortho 10. 🟢
- RN-26 (R24): 3D — alvo = média dos centros das paredes; câmera em alvo + (8, −8, 8); PERSP 35 mm ou ORTHO 10; câmera não travada. 🟢
- RN-27 (R25): multivista em cruz — Front em (0,0); Plan acima; Back acima do Plan; Left/Right laterais; gap 12"; `ortho = max(W, H) + 2·6"`; câmera a z=10. 🟢
- RN-28 (R26): instâncias cancelam a rotação de mundo da origem (`rot = Euler(base) @ R_origem⁻¹`). 🟢
- RN-29 (R27): linhas ocultas da multivista — peças internas vão para `Content Dashed` só se a abertura de face frame ancestral tiver `front_type ≠ 'NONE'`; tracejado só em células de elevação. 🟢
- RN-30 (R28): prancha iso-left — iso θ=−60°; maior escala da escada `1/2", 3/8", 1/4", 3/16", 1/8" = 1'` que caiba (margens 0,5", base 1,5"), senão 1/8"; grava `hb_paper_size`, `hb_paper_landscape`, `hb_layout_scale`. 🟢

**Carimbo**
- RN-31 (R31): `camera.scale = ortho_scale`; retângulo-âncora oculto; 4 textos (Project Name, Designer Name, Scale, Page Number) com placeholders em inglês, tamanho 0,015, espaçados 0,5"; na collection IGNORE. 🟢
- RN-32 (R32): `TitleBlock.update` não reconhece nenhum campo criado — inoperante. 🟡

**Detalhes 2D e biblioteca**
- RN-33 (R33): cena de detalhe com nome único (`Detail 1`, …); salva o estado da vista se a origem for cômodo; viewport top-down SOLID/OBJECT. 🟢
- RN-34 (R34): primitivas — linha/círculo pretos `bevel_depth` 0,002; polilinha usa espessura/cor da cena; círculo 32 segmentos cíclico; texto `extrude` 0,001, tamanho 0,05, LEFT/BOTTOM; tags `IS_DETAIL_*` + `IS_2D_ANNOTATION`. 🟢
- RN-35 (R35): fonte do rótulo — `annotation_font` > Calibri do Windows > Bfont; cor aplicada ao objeto e ao material compartilhado `HB Label Text`. 🟢
- RN-36 (R36): salvar detalhe exige cena `IS_DETAIL_VIEW`/`IS_CROWN_DETAIL` e ≥ 1 CURVE/FONT/MESH; arquivo `<nome sanitizado>_<AAAAMMDD_HHMMSS>.blend` com `fake_user`; tipo `crown` ou `detail`. 🟢
- RN-37 (R37): a listagem descarta entradas sem arquivo e recalcula `filepath`; filtro opcional por tipo. 🟢
- RN-38 (R38): excluir apaga o arquivo e filtra o índice; sempre retorna sucesso. 🟢

**Assets**
- RN-39 (R39): biblioteca embutida "Home Builder" → `blendertomob/assets`; do usuário `HB: <nome> [<id 12 hex>]`, `APPEND`; bibliotecas `HB: ` órfãs e "Home Builder Extended" legado são removidas. 🟢
- RN-40 (R40): caminhos de conteúdo por subpasta — embutido primeiro, depois as do usuário, sem duplicatas (`moldings/`, `cabinet_pulls/`, `cabinet_groups/`). 🟢
- RN-41 (R41): catálogos lidos de `blender_assets.cats.txt` (`uuid:caminho[:nome]`); atribuir catálogo aplica o UUID a todo asset marcado do arquivo. 🟢
- RN-42 (R42): asset shelf "home_builder" só no modo OBJECT, para OBJECT/COLLECTION/MATERIAL; prévia 96 px. 🟢

**Comportamentos desconhecidos**
- 🔴 O exportador híbrido (OpenGL GP + F12 Freestyle) citado nas docstrings não foi localizado; `setup_iso_freestyle`, `build_line_art_marked_channel`, `build_line_art_text_holdouts` não têm chamador.
- 🔴 Preenchimento real dos campos do carimbo (nome do projeto, projetista, "PAGE 1 OF 12" fixo) não ocorre nesta unit.
- 🔴 Miniaturas prometidas na docstring de `hb_detail_library` não existem.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Criar cena de prancha com unidades, snap, render e collections de roteamento | Must | Cena `IS_LAYOUT_VIEW` com 3 collections e `HB_LINE_ENGINE` |
| RF-02 | Configurar papel (tamanho, orientação, DPI) e resolução | Must | LETTER paisagem 150 DPI → 1650×1275 |
| RF-03 | Traço Freestyle com linesets Solid e Dashed | Must | Peça interna aparece tracejada no render |
| RF-04 | Traço Line Art com câmera jitter e espessuras por escala | Should | Mudar a escala da prancha muda a espessura no mundo |
| RF-05 | Elevação de parede com câmera, enquadramento e cotas de gabinetes | Must | Todos os gabinetes da parede e suas cotas dentro do quadro |
| RF-06 | Atualizar elevação existente | Should | Câmera reposicionada após mudar o comprimento da parede |
| RF-07 | Criar elevações de todas as paredes | Should | Uma cena por `IS_WALL_BP` |
| RF-08 | Planta baixa | Must | Todas as paredes da cena de origem visíveis |
| RF-09 | Vista 3D perspectiva/ortográfica | Should | Câmera olhando o centro das paredes |
| RF-10 | Multivista em cruz de um objeto | Should | Células nas posições de RN-27 com rotação cancelada |
| RF-11 | Prancha iso + planta + elevação com escala automática | Could | Escala escolhida é a maior que cabe |
| RF-12 | Carimbo com 4 campos | Should | Textos na collection IGNORE, dentro da área da câmera |
| RF-13 | Preencher campos do carimbo com dados do projeto | Should | 🔴 hoje não ocorre — ver Q-03 |
| RF-14 | Assar/desassar Line Art | Could | Após bake, strokes editáveis e modificadores desligados; unbake restaura |
| RF-15 | Obter a vista a partir da cena (fábrica) | Must | `get_layout_view_from_scene` devolve a classe correta pela tag |
| RF-16 | Excluir prancha | Should | Cena removida — hoje deixa collections/câmera/GP órfãos |
| RF-17 | Cena de detalhe 2D e primitivas | Must | Linha, polilinha, círculo e texto criados com tags e materiais |
| RF-18 | Salvar detalhe na biblioteca do usuário | Should | Arquivo `.blend` + entrada no `library_index.json` |
| RF-19 | Listar/carregar/excluir detalhes | Should | Entradas sem arquivo não aparecem; carregar traz os objetos para a cena atual |
| RF-20 | Registrar bibliotecas de assets (embutida + usuário) | Must | Preferências contêm "Home Builder" apontando para `assets/` |
| RF-21 | Adicionar/remover/atualizar biblioteca do usuário | Should | Operadores refletem a lista nas preferências |
| RF-22 | Atribuir catálogo a assets do arquivo | Could | UUID aplicado a todos os assets marcados |
| RF-23 | Asset shelf "home_builder" | Should | Visível só no modo OBJECT |
| RF-24 | Canal Marked, holdout de texto e vista híbrida iso | Won't | Sem chamador; manter congelado até decidir (Q-01) |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Cenas de prancha instanciam collections em vez de copiar objetos | `hb_layouts.py:1681-1734` | 🟢 |
| Performance | Bake de Line Art para evitar recalcular oclusão a cada redesenho | `hb_layouts.py:255-346` | 🟢 |
| Qualidade de saída | Resolução por DPI (150) e AA 32 | `hb_layouts.py:21,1194-1210,1384-1410` | 🟢 |
| Persistência | Biblioteca de detalhes em `extension_path_user(__package__, "detail_library", create=True)` | `hb_detail_library.py:16` | 🟢 |
| Robustez | Índice JSON corrompido → índice vazio (sem travar) | `hb_detail_library.py:28-35` | 🟢 |
| Robustez | Troca de `window.scene` no bake com `try/finally` | `hb_layouts.py:255-330` | 🟢 |
| Compatibilidade | Fallback por `TypeError` em `layer.frames.remove` (API GP v3 variou) | `hb_layouts.py:244-252` | 🟢 |
| Portabilidade | Fonte Calibri procurada só em pastas do Windows | `hb_details.py:308-381` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Elevação de parede

  Cenário: Elevação com gabinetes inferiores e aéreos
    Dado uma parede de 3 m com 2 inferiores (z=0) e 1 aéreo (z=1,4 m)
    Quando ElevationView().create(parede) é executado
    Então existe uma cena IS_LAYOUT_VIEW e IS_ELEVATION_VIEW com SOURCE_WALL = parede
    E há 3 cotas: duas a z=-4" e uma acima do topo do aéreo + 4"
    E a câmera ORTHO enquadra parede, gabinetes e cotas com margem de 10%

  Cenário: Parede sem gabinetes
    Dado uma parede vazia
    Quando a elevação é criada
    Então não há cotas e o enquadramento cobre [0,L]×[0,H] com margem

Funcionalidade: Papel

  Cenário: Tamanho desconhecido
    Dado PAPER_SIZE = "B5"
    Quando set_paper_size é aplicado
    Então a resolução é a do LETTER
    Mas scene["PAPER_SIZE"] continua gravado como "B5"

  Cenário: Paisagem
    Dado A4 paisagem a 150 DPI
    Quando set_paper_size é aplicado
    Então resolution_x = 1753 e resolution_y = 1240 (int() trunca 1753,5 e 1240,5)

Funcionalidade: Engine de linha

  Cenário: Preferência Line Art
    Dado a preferência line_engine = LINEART
    Quando uma elevação é criada
    Então existe um objeto GP IS_HB_LINEART com 2 camadas e 4 modificadores
    E scene["HB_LINE_ENGINE"] = "LINEART"

  Cenário: Vista 3D ignora Line Art
    Dado a preferência line_engine = LINEART
    Quando View3D().create() é executado
    Então a cena usa Freestyle e não tem objeto GP

Funcionalidade: Bake de Line Art

  Cenário: Bake com strokes
    Dado uma cena Line Art com geometria visível
    Quando bake_line_art_editable(scene) é chamado
    Então retorna True, todos os modificadores ficam desligados e HB_LINEART_BAKED é marcado

  Cenário: Bake sem GP
    Dado uma cena Freestyle
    Quando bake_line_art_editable(scene) é chamado
    Então retorna False sem alterar a cena

Funcionalidade: Biblioteca de detalhes

  Cenário: Salvar detalhe
    Dado uma cena IS_DETAIL_VIEW com 3 curvas
    Quando save_detail_to_library(context, "Rodapé 7cm") é chamado
    Então é criado "Rodap__7cm_<data>.blend" e o índice ganha uma entrada detail

  Cenário: Salvar fora de cena de detalhe
    Dado uma cena de cômodo
    Quando save_detail_to_library é chamado
    Então retorna (False, mensagem, "") e nada é gravado

  Cenário: Arquivo apagado manualmente
    Dado uma entrada no índice cujo .blend não existe
    Quando get_library_details() é chamado
    Então a entrada não aparece na lista

Funcionalidade: Bibliotecas de assets

  Cenário: Registro
    Dado a extensão sendo ativada
    Quando ensure_asset_libraries() roda
    Então as preferências têm "Home Builder" → blendertomob/assets
    E bibliotecas "HB: " sem id conhecido são removidas
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Cena de prancha, papel, Freestyle, elevação, planta, fábrica (RF-01..RF-03, RF-05, RF-08, RF-15) | Must | Entregável principal do projetista (pranchas) |
| Detalhe 2D (RF-17) e bibliotecas de assets (RF-20) | Must | Usados por operadores e pela asset shelf em toda sessão |
| Line Art, update, todas as elevações, 3D, multivista, carimbo, exclusão, biblioteca de detalhes, gestão de libs, shelf (RF-04, RF-06..RF-10, RF-12, RF-13, RF-16, RF-18, RF-19, RF-21, RF-23) | Should | Importantes, com alternativa |
| Iso-left, bake, catálogos (RF-11, RF-14, RF-22) | Could | Uso pontual |
| Canal Marked, holdout, vista híbrida (RF-24) | Won't | Sem chamador |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `hb_layouts.py` | `PAPER_SIZES`, `DEFAULT_DPI`, constantes Line Art | 🟢 |
| `hb_layouts.py` | `get_default_line_engine`, `setup_line_art_for_scene`, `update_line_art_sizes`, `bake_line_art_editable`, `unbake_line_art`, `set_line_art_visible`, `refresh_line_art` | 🟢 |
| `hb_layouts.py` | `build_line_art_marked_channel`, `build_line_art_text_holdouts`, `setup_iso_freestyle` | 🟢 (sem chamador) |
| `hb_layouts.py` | `TitleBlock`, `LayoutView`, `ElevationView`, `PlanView`, `View3D`, `MultiView` | 🟢 |
| `hb_layouts.py` | `get_layout_view_from_scene`, `create_all_elevations` | 🟢 |
| `hb_details.py` | `DetailView`, `GeoNodeLine`, `GeoNodePolyline`, `GeoNodeCircle`, `GeoNodeText`, fonte/material de rótulo | 🟢 |
| `hb_detail_library.py` | `save_detail_to_library`, `get_library_details`, `load_detail_from_library`, `get_detail_info`, `delete_detail_from_library` | 🟢 |
| `hb_assets.py` | `ensure_asset_libraries`, caminhos de conteúdo, catálogos, operadores `home_builder.*_asset_library`, `assign_asset_catalog`, asset shelf, `BTM_AssetLibraryEntry` | 🟢 |
