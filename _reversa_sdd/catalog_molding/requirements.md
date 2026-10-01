# catalog_molding — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-catalog_molding`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#catalog_molding`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-catalog_molding-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Visão Geral

Dois subsistemas independentes agrupados numa unit:

1. **`catalog/`** — navegador de produtos num painel lateral ("Catalog"), com busca fuzzy, filtro por categoria,
   lista/grade com miniaturas e botão de colocação. **Não é registrado pelo add-on**: é código latente. Das 78 entradas,
   só 7 têm operador real; 71 são stubs. 🟢
2. **`molding/`** — pacotes de moldura por ambiente (crown, rodapé/base, light rail e furniture cap). O usuário escolhe os
   pacotes na sala e o sistema limpa e reconstrói todas as molduras da cena, varrendo perfis 2D por caminhos que encadeiam
   gabinetes contíguos, contornam cantos em L, envolvem ilhas, pulam eletrodomésticos e retornam em laterais acabadas. 🟢

## Responsabilidades

**Catálogo**
- Listar produtos colocáveis com id estável, categoria hierárquica, busca e reordenação contextual. 🟢
- Resolver miniaturas (arquivo, `{id}.png`, placeholder) e renderizar miniaturas Workbench. 🟢
- Disparar o operador de colocação e aplicar o estilo ativo ao produto colocado. 🟢

**Molduras**
- Coletar alvos elegíveis por tipo de moldura e por biblioteca (face frame, frameless). 🟢
- Agrupar gabinetes em corridas, ordenar cadeias e calcular caminhos com meia-esquadria. 🟢
- Tratar cantos em L, ilhas, eletrodomésticos de piso (bridges), rodapés recuados e pontas acabadas. 🟢
- Empilhar perfis (pacotes), calcular a cota Z de cada sweep e criar as curvas com perfil e material. 🟢
- Reconstruir tudo quando um pacote muda; refazer sob comando quando os gabinetes mudam. 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `CATALOG_MOLDING-Rnn`).

**Catálogo**
- RN-01 (R01): id = `categoria (com / → _) + '_' + nome sanitizado`. 🟢
- RN-02 (R02/R03): todas as entradas são `kind='product'` (verbo "Place at cursor"); estilos, acabamentos e inserts não fazem parte do catálogo (são modificações de gabinetes). 🟢
- RN-03 (R04/R05): 7 entradas chamam `hb_face_frame.draw_cabinet`; 71 stubs colocam um gabinete face frame genérico pelo nome (Upper/Wall → Upper; Tall/Pantry/Oven → Tall; senão Base Door). 🟢
- RN-04 (R06): após colocar, aplica o estilo ativo da cena ao `context.active_object` — provavelmente o objeto errado, porque o operador só abre um modal. 🟢 / 🟡
- RN-05 (R07/R08): categoria casa a própria e as descendentes; busca por substring ou subsequência fuzzy em código + nome + descrição. 🟢
- RN-06 (R09): reordenação contextual por `kind` (hoje inócua, pois tudo é `product`). 🟢
- RN-07 (R10/R11/R12): miniatura por arquivo → `{id}.png` → placeholder; só itens com operador real são renderizáveis; câmera az −45°, el 25°, distância 2× o maior lado, Workbench 256×256 transparente. 🟢

**Molduras — alvos e corridas**
- RN-08 (R14): CROWN/CAP em UPPER e TALL; BASE em BASE, TALL e LAP_DRAWER; LIGHT_RAIL em UPPER. Closets não têm adaptador. 🟢
- RN-09 (R15): eletrodomésticos de piso (`z ≤ 0,02 m`) entram nas corridas de BASE como bridges (rodapé pulado, forçam retornos). 🟢
- RN-10 (R16/R17): membros se tocam se os AABBs de planta (+0,02 m) se sobrepõem e a cota de alinhamento coincide (±0,02 m); componentes conexos por BFS; cadeia começa num membro com 1 vizinho. 🟢

**Molduras — geometria**
- RN-11 (R18/R19): offset à direita com meia-esquadria; colineares viram degrau; sentido normalizado para o offset sair para fora. 🟢
- RN-12 (R20): canto em L com frente `(ld,−depth) → (ld,−rd) → (width,−rd)` (ou diagonal); `ld/rd` ausentes → 24". 🟢
- RN-13 (R21): ponta acabada recebe retorno até o canto traseiro; não acabada termina rente (face frame pela condição de ponta; frameless por sonda de parede a 0,03 m). 🟢
- RN-14 (R22/R23): rodapé por spans — eletrodoméstico → SKIP; sem recuo → FRONT; recuado → stiles FRONT em L e trecho RECESS; trechos consecutivos retornam nas fronteiras. 🟢
- RN-15 (R24): ilha = cadeia sem parent, sem canto, com ≤ 2 rotações opostas; perímetro fechado quando tudo é mantido. 🟢

**Molduras — pilhas, cotas e perfis**
- RN-16 (R25/R27): pilhas de perfis com `STACK_FRONT`/`STACK_OFFSET` e override por categoria; base shoe e furniture cap independentes. 🟢
- RN-17 (R26): cota Z — CROWN = datum + dy (face frame: altura − top rail + overlay + reveal; frameless: altura); CAP acima do topo da pilha crown; BASE/LIGHT_RAIL = dy. 🟢
- RN-18 (R28/R29): perfil de pack `.blend` ou contorno embutido; perfis ocultos, 2D, marcados; métricas com cache. 🟢
- RN-19 (R30): material = acabamento do primeiro membro que resolver. 🟢
- RN-20 (R31): qualquer mudança de pacote limpa e recria todas as molduras; mudanças de gabinete exigem "Refresh Molding". 🟢
- RN-21 (R32): itens de enum de pacotes e perfis cacheados no módulo. 🟢

**Comportamentos desconhecidos**
- 🔴 Por que `catalog/` não é registrado (abandono, substituição pelo `hb_assets`, esquecimento).
- 🔴 Operador `hb_catalog.render_thumbnail` nunca implementado.
- 🔴 Ausência de adaptador de molduras para `closets` (intencional?).
- 🔴 Nenhum pack de perfis no repositório; formato real é só convenção.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Pacotes de moldura por ambiente (crown, base, light rail, cap, base shoe) | Must | Escolher "SIMPLE" em crown cria sweeps sobre todos os aéreos/altos |
| RF-02 | Corridas e cadeias de gabinetes contíguos | Must | Três aéreos encostados → um sweep contínuo |
| RF-03 | Meia-esquadria, cantos em L e degraus | Must | Canto em L com moldura contínua mitrada |
| RF-04 | Retornos em pontas acabadas | Must | Ponta acabada → retorno até a parede |
| RF-05 | Rodapé com spans (pula eletrodomésticos, recesso opcional) | Must | Lava-louças no meio interrompe o rodapé com retornos |
| RF-06 | Ilhas com perímetro fechado | Should | Ilha costas-com-costas → laço fechado |
| RF-07 | Pilhas de perfis e cota Z por tipo | Must | Crown STACKED = spacer + crown alinhados |
| RF-08 | Perfis de pack `.blend` ou contornos embutidos | Should | Sem pack → contorno embutido |
| RF-09 | Material do acabamento do gabinete | Should | Sweep com o material do estilo do primeiro membro |
| RF-10 | Refazer molduras sob comando | Must | "Refresh Molding" reconstrói a partir do estado atual |
| RF-11 | Molduras em closets | Should | Starter de closet recebe crown (hoje sem adaptador) |
| RF-12 | Navegador de catálogo de produtos | Could | Painel com busca, categorias e grade (hoje não registrado) |
| RF-13 | Colocar produto pelo catálogo e aplicar o estilo ao objeto colocado | Could | Estilo aplicado ao gabinete criado, não ao ativo anterior |
| RF-14 | Miniaturas do catálogo | Could | Render grava em `extension_path_user` |
| RF-15 | 71 entradas stub do catálogo | Won't | Stubs não são produtos reais |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Idempotência | Reconstrução total e determinística das molduras | `molding/ops.py:246-297` | 🟢 |
| Desacoplamento | Geometria agnóstica de biblioteca (`engine`) + adaptadores por biblioteca | `molding/engine.py`; `molding/adapters.py` | 🟢 |
| Compatibilidade | Enums dinâmicos cacheados (molduras); sem cache (catálogo) | `molding/packages.py:55-58`; `catalog/props_catalog.py:24-28` | 🟢 |
| Robustez | Erros do callback de pacote só vão para `print` | `molding/ops.py:300-307` | 🟢 |
| Recursos | Timer do catálogo não cancelado no `unregister` | `catalog/props_catalog.py:148-154` | 🟢 |
| Persistência | Miniaturas gravadas na pasta do add-on (não em `extension_path_user`) | `catalog/render_thumbnails.py:36-37` | 🟢 |
| Desempenho | Reconstrução pesada dentro de `update=` (cria/remove objetos, `libraries.load`) | `hb_props.py:164-168` → `molding/ops.py:300-307` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Molduras por ambiente

  Cenário: Crown contínua
    Dado três aéreos encostados com topos alinhados
    Quando o pacote de crown muda para SIMPLE
    Então existe um único sweep IS_HB_MOLDING_SWEEP cobrindo os três

  Cenário: Ponta acabada
    Dado a ponta direita da corrida com lateral acabada
    Então a moldura retorna até o canto traseiro dessa ponta

  Cenário: Eletrodoméstico no rodapé
    Dado um lava-louças de piso entre dois inferiores
    Quando o pacote de base é aplicado
    Então o rodapé é interrompido no lava-louças com retornos nos dois lados

  Cenário: Ilha
    Dado uma ilha costas-com-costas sem parent
    Então o rodapé forma um laço fechado

  Cenário: Gabinete alterado
    Dado molduras aplicadas
    Quando um aéreo muda de largura
    Então as molduras não mudam até "Refresh Molding" (comportamento legado)

  Cenário: Cena de layout
    Dado a cena ativa marcada IS_LAYOUT_VIEW
    Quando apply_scene_packages roda
    Então nada é criado

Funcionalidade: Catálogo (se reativado)

  Cenário: Busca fuzzy
    Dado o item "Upper Stacked"
    Quando o usuário busca "upstk"
    Então o item aparece (subsequência)

  Cenário: Stub
    Quando o usuário coloca "Double Oven cabinet" (stub)
    Então um gabinete face frame Tall genérico é colocado
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Pacotes, corridas, geometria, retornos, rodapé, pilhas, refresh — RF-01..RF-05, RF-07, RF-10 | Must | Subsistema registrado e em uso |
| Ilhas, packs de perfis, material, closets — RF-06, RF-08, RF-09, RF-11 | Should | Importantes, com alternativa |
| Catálogo, colocação, miniaturas — RF-12..RF-14 | Could | Código não registrado; destino depende de Q-01 |
| Stubs do catálogo — RF-15 | Won't | Não são produtos |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `molding/ops.py` | `apply_scene_packages`, `_apply_type`, `_spawn_sweep`, `clear_scene_molding`, `on_package_changed`, `blendertomob.refresh_room_molding` | 🟢 |
| `molding/engine.py` | corridas, cadeias, offsets, cantos, rodapé, ilhas | 🟢 |
| `molding/adapters.py` | alvos, bridges, FACTS (face frame, frameless) | 🟢 |
| `molding/packages.py` | presets, packs, contornos embutidos, métricas | 🟢 |
| `catalog/*.py` | `CATALOG`, `HBCatalogState`, previews, `hb_catalog.activate_item`, render de miniaturas, UI | 🟢 (não registrado) |
| `hb_props.py:164-208`, `:493-580` | 13 props `molding_*` com `update` | 🟢 |
