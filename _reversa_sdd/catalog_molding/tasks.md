# catalog_molding — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Pré-requisitos
- [ ] Decisão sobre a **consolidação das três implementações de moldura** (Q-02): `molding/`, `frameless/operators/ops_crown|toe_kick|upper_bottom.py`
      e `closets/molding_closets.py`.
- [ ] Decisão sobre o destino do `catalog/` (Q-01).
- [ ] Preset de medidas BR/EUA (`product_common` Q-06) para contornos e defaults.
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]` (confirmar `fill_mode='NONE'` com `dimensions='2D'`).

## Tarefas

### Bloco A — Motor de molduras

- [ ] T-01, `engine` puro: corridas, cadeias, offsets com meia-esquadria, canto em L, spans de rodapé, ilhas
  - Origem no legado: `molding/engine.py:35-730`
  - Critério de pronto: testes sem Blender (entradas como dicts); RN-10..RN-15
  - Confiança: 🟢

- [ ] T-02, Adaptadores por biblioteca com interface comum (alvos, bridges, facts, material), incluindo **closets**
  - Origem no legado: `molding/adapters.py:16-230`
  - Critério de pronto: um adaptador por linha (frameless, face frame, closets); RN-08, RN-09, RN-13
  - Confiança: 🟢 (existentes) / 🔴 (closets, Q-03)

- [ ] T-03, Pilhas de perfis e cotas Z por tipo
  - Origem no legado: `molding/ops.py:46-123`, `:226-243`
  - Critério de pronto: RN-16, RN-17
  - Confiança: 🟢

- [ ] T-04, `_spawn_sweep` sem órfãos: remover também a curva quando não há splines; identificar membros por lista (não string separada por vírgula)
  - Origem no legado: `molding/ops.py:126-187`
  - Critério de pronto: aplicar e limpar 10× não deixa curvas nem perfis órfãos
  - Confiança: 🟢

- [ ] T-05, Packs de perfis e contornos embutidos (valores do preset), limpando materiais auxiliares do append
  - Origem no legado: `molding/packages.py:24-347`
  - Critério de pronto: RN-18; contagem de materiais estável após carregar um pack
  - Confiança: 🟢 (estrutura) / 🟡 (pacotes BR, Q-05)

### Bloco B — Orquestração

- [ ] T-06, `apply_scene_packages` fora do callback `update=`: o callback só agenda a reconstrução (timer) e erros viram aviso visível
  - Origem no legado: `hb_props.py:164-168`; `molding/ops.py:246-307`
  - Critério de pronto: mudar um pacote não bloqueia a UI; erro aparece no cabeçalho/relatório
  - Confiança: 🟢

- [ ] T-07, Operador de refresh com `UNDO` e indicação de "molduras desatualizadas" quando um gabinete da corrida muda
  - Origem no legado: `molding/ops.py:310-319`
  - Critério de pronto: alterar um gabinete marca as molduras; refresh refaz; Ctrl+Z desfaz
  - Confiança: 🟡 (Q-04)

- [ ] T-08, `register()`/`unregister()` sem engolir exceções
  - Origem no legado: `molding/ops.py:327-348`
  - Critério de pronto: registrar/desregistrar 2× sem resíduo
  - Confiança: 🟢

- [ ] T-09, Consolidar as molduras do frameless (crown, rodapé, moldura inferior) e do closets no motor `molding/`
  - Origem no legado: `product_libraries/frameless/operators/ops_crown.py`, `ops_toe_kick.py`, `ops_upper_bottom.py`; `product_libraries/closets/molding_closets.py`
  - Critério de pronto: uma única implementação; os operadores antigos viram atalhos para ela
  - Confiança: 🟡 (Q-02)

### Bloco C — Catálogo (condicional a Q-01)

- [ ] T-10, Decidir: registrar o `catalog/` corrigido, substituí-lo pelo asset browser (`hb_assets`) ou removê-lo
  - Origem no legado: `catalog/` inteiro; `blendertomob/__init__.py:9-57`
  - Critério de pronto: decisão aplicada; nenhum código morto no pacote
  - Confiança: 🔴 (Q-01)

- [ ] T-11, (se mantido) Catálogo gerado das bibliotecas reais (sem stubs), com busca fuzzy e categorias
  - Origem no legado: `catalog/catalog_data.py`, `ui_catalog.py:21-124`
  - Critério de pronto: só produtos colocáveis aparecem; RN-05
  - Confiança: 🟡

- [ ] T-12, (se mantido) Aplicar o estilo ao objeto **criado** pela colocação (callback ao fim do modal), não ao ativo
  - Origem no legado: `catalog/ops_catalog.py:16-86`
  - Critério de pronto: estilo aplicado ao gabinete novo
  - Confiança: 🟡

- [ ] T-13, (se mantido) Miniaturas em `extension_path_user`, operador `render_thumbnail` real, render sem depender de `context.window` e com `studio_light` validado
  - Origem no legado: `catalog/render_thumbnails.py`; `ui_catalog.py:275-280`
  - Critério de pronto: render em `--background`; painel não quebra ao selecionar item
  - Confiança: 🟢

- [ ] T-14, (se mantido) Timer cancelado no `unregister`; enum de categorias com cache
  - Origem no legado: `catalog/props_catalog.py:24-28`, `:114-154`
  - Critério de pronto: `unregister()` com sync pendente não gera erro
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Engine puro: corridas, cadeia com ramificação, offsets colineares, canto em L, ilha costas-com-costas
- [ ] TT-02, Rodapé com lava-louças e recesso (`include_recessed` ligado/desligado)
- [ ] TT-03, Pilha STACKED e cota Z de CROWN/CAP para face frame e frameless
- [ ] TT-04, Idempotência: aplicar 10× produz o mesmo resultado e nenhum órfão
- [ ] TT-05, Cena de layout ignorada
- [ ] TT-06, Adaptador de closets (T-02)
- [ ] TT-07, (se catálogo mantido) busca fuzzy, stub, render em background

## Tarefas de Migração de Dados

- [ ] TM-01, Arquivos com molduras das implementações antigas (frameless/closets): converter para sweeps do motor único ou manter como estáticos marcados
  - Origem: `ops_crown.py`, `molding_closets.py`
  - Confiança: 🟡 (Q-02)
- [ ] TM-02, Preservar as 13 props `molding_*` da sala
  - Confiança: 🟢

## Ordem Sugerida
1. Responder **Q-02** (consolidação) — define o escopo do Bloco A.
2. **Bloco A** (engine puro e adaptadores) e **B** (orquestração).
3. **T-09** (consolidação) depois que A e B estiverem estáveis.
4. **Bloco C** só se Q-01 decidir manter o catálogo.
5. Bloqueios: T-10..T-14 ← Q-01; T-09/TM-01 ← Q-02; T-02 (closets) ← Q-03; T-07 ← Q-04; T-05 ← Q-05.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 2 (2026-10-01) — ver **Decisões da rodada 2** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Destino do catálogo.
- Q-02 Consolidação das três implementações de moldura.
- Q-03 Molduras em closets.
- Q-04 Atualização automática × "desatualizada".
- Q-05 Pacotes e perfis brasileiros.

## Decisões da rodada 2 (2026-10-01)

Todas as recomendações ⭐ foram aceitas. As tarefas listadas saem do estado bloqueado e seguem a decisão.

| Pergunta | Decisão | Tarefas desbloqueadas |
|---|---|---|
| Q-01 | Substituir: uma biblioteca de módulos única, gerada das linhas de produto reais, com busca ("Localizar Rápido") e favoritos; remover o `catalog/`. | T-10..T-14 |
| Q-02 | Sim: o motor `molding/` (engine + adaptadores) vira o único; os operadores antigos passam a usá-lo. | T-09, TM-01 |
| Q-03 | Sim (adaptador de closets no motor único). | T-02 |
| Q-04 | Marcar desatualizadas com refazer em 1 clique (mesma decisão sugerida para bancadas em `frameless` Q-05). | T-07 |
| Q-05 | Rodapé reto 70/100/150 mm em MDF 15/18 mm, sanca simples e perfil de LED (light rail) como pacotes padrão; perfis americanos como pack opcional. | T-05 |
