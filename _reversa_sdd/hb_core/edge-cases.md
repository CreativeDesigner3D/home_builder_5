# hb_core — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

---

## EC-01 — Calculadora com valores fixos maiores que o total 🟢
- **Cenário:** vão de 600 mm com duas divisórias fixas de 400 mm e um prompt "igual".
- **Comportamento legado:** `valor = (0,6 − 0,8) / 1 = −0,2 m` é gravado no prompt, sem checagem (`hb_props.py:294-320`).
- **Impacto:** drivers dependentes recebem altura negativa → peças invertidas ou com malha degenerada no GN.
- **Mitigação:** manter o valor para paridade, mas emitir aviso (`self.report`/overlay) e destacar a calculadora; opcionalmente limitar a 0 atrás de uma preferência. 🟡

## EC-02 — Calculadora sem prompts "iguais" 🟢
- **Cenário:** todos os prompts fixos.
- **Comportamento legado:** retorna cedo; a soma dos fixos pode não fechar com o total e nada avisa.
- **Impacto:** sobra ou falta de espaço silenciosa no vão.
- **Mitigação:** calcular `folga = total − Σ fixos` e expô-la na UI. 🟡

## EC-03 — Cache de socket com `id()` reciclado 🟡
- **Cenário:** node group apagado e outro criado na mesma posição de memória (mesmo `id()` do wrapper Python).
- **Comportamento legado:** o cache devolve o identificador do grupo antigo; se o identificador existir no novo grupo, a escrita vai para o socket **errado** sem exceção (o retry só dispara em `KeyError`/`AttributeError`) (`hb_types.py:24-50`).
- **Impacto:** medida escrita no input errado, sem erro visível.
- **Mitigação:** chave estável (T-02) ou validação do nome do socket antes de usar o identificador em cache.

## EC-04 — Arquivo salvo no Blender < 5.2 aberto no 5.2 🔴
- **Cenário:** projeto antigo com drivers em `modifiers["GeoNodes"]["Socket_2"]`.
- **Comportamento legado:** nenhum código reescreve os caminhos (`hb_utils.py:55-60` só gera caminhos novos).
- **Impacto:** drivers inválidos (sublinhados em vermelho) → gabinetes deixam de acompanhar as medidas.
- **Mitigação:** migração em `load_post` (TM-01), condicionada à resposta de Q-02.

## EC-05 — Driver de location/rotation com eixo inválido 🟢
- **Cenário:** `driver_location('X', ...)` (maiúsculo) ou `'w'`.
- **Comportamento legado:** `UnboundLocalError`, porque o índice só é atribuído para `x/y/z` (`hb_types.py:211-233`).
- **Impacto:** exceção pouco clara que interrompe a construção do produto.
- **Mitigação:** normalizar para minúsculas e levantar `ValueError("eixo inválido")`.

## EC-06 — Registro de PropertyGroup falha em silêncio 🟢
- **Cenário:** erro de anotação em um `bpy.props` ou conflito com versão antiga carregada.
- **Comportamento legado:** `except Exception: pass` em todos os `register()` (`hb_props.py:955-966`, `hb_project.py:290-305`, `hb_props_obstacles.py:277-292`, `ops.py:664-675`).
- **Impacto:** o sintoma surge longe da causa (`'Object' object has no attribute 'home_builder'`).
- **Mitigação:** registrar a exceção (traceback) e relançar, exceto no caso específico "já registrado".

## EC-07 — `unregister()` com modal de escala ativo 🟢
- **Cenário:** usuário desativa a extensão durante `set_scale_with_two_points`.
- **Comportamento legado:** o draw handler só é removido em `cleanup()` (término/cancelamento), não em `unregister()` (`ops.py:588-594`).
- **Impacto:** callback órfão apontando para código descarregado → erro a cada redesenho.
- **Mitigação:** guardar o handle em variável de módulo e removê-lo em `unregister()`; implementar `cancel()`.

## EC-08 — `driver_namespace` acumulado após recarregar a extensão 🟢
- **Cenário:** desativar e reativar a extensão várias vezes.
- **Comportamento legado:** `IF/OR/AND` e dunders do módulo (`__name__`, `__doc__` …, via `inspect.getmembers`) nunca são removidos; como a injeção só ocorre se o nome não existir, a versão **antiga** da função permanece após recarregar (`__init__.py:68-70,254-256`).
- **Impacto:** correções em `hb_driver_functions.py` não entram em vigor até reiniciar o Blender; namespace poluído.
- **Mitigação:** injetar apenas os três nomes, sobrescrever sempre e remover em `unregister()` (T-06).

## EC-09 — Cena principal em contexto de desenho 🟢
- **Cenário:** `get_main_scene()` chamado de um `Panel.draw` quando nenhuma cena tem `IS_MAIN_SCENE`.
- **Comportamento legado:** escolhe a cena pelas regras de fallback, tenta marcar e engole `AttributeError` (`hb_project.py:170-174`).
- **Impacto:** a cena escolhida pode mudar entre chamadas até que um operador a marque (ex.: reordenar cômodos muda `sort_order`) → dados de projeto parecem "sumir".
- **Mitigação:** marcar sempre em `load_post` (já feito por `ensure_main_scene`) e em todo operador que cria/apaga cenas.

## EC-10 — Duas definições de "cena de cômodo" 🟢
- **Cenário:** cena de detalhe de coroa (`IS_CROWN_DETAIL`).
- **Comportamento legado:** `hb_project.is_room_scene` a considera cômodo; `hb_utils.is_room_scene` não (`hb_project.py:265-271`, `hb_utils.py:461-469`).
- **Impacto:** a cena de detalhe pode virar "cena principal" ou aparecer na lista de cômodos, dependendo do chamador.
- **Mitigação:** uma única função (T-18).

## EC-11 — Cadeia de paredes fechada 🟢
- **Cenário:** cômodo fechado de 4 paredes; um percorredor chama `get_connected_wall('right', include_loop_seam=True)` em laço.
- **Comportamento legado:** o vizinho geométrico atravessa a emenda e o laço volta à primeira parede para sempre; a docstring alerta que percorredores devem usar `False` (`hb_types.py:486-503`).
- **Impacto:** travamento do Blender.
- **Mitigação:** percorredores guardam o conjunto de paredes visitadas, independentemente do parâmetro.

## EC-12 — Paredes que só compartilham um canto 🟢
- **Cenário:** dois cômodos distintos cujas paredes se tocam num ponto (tolerância 0,01 m).
- **Comportamento legado:** `_geometric_neighbor` as considera vizinhas (`hb_types.py:524-561`).
- **Impacto:** posicionamento sensível a cantos pode "puxar" gabinete para o cômodo vizinho. Intencional segundo a docstring.
- **Mitigação:** manter; documentar para `hb_placement`.

## EC-13 — Cota em sistema imperial com pés 🟡
- **Cenário:** cena com `unit_settings.system = 'IMPERIAL'` e `length_unit = 'FEET'`.
- **Comportamento legado:** `get_unit_type()` retorna 0 (polegadas); `Unit Type = 1` nunca é produzido (`hb_types.py:693-712`).
- **Impacto:** cotas exibem polegadas mesmo com a cena em pés.
- **Mitigação:** mapear `FEET → 1`; decidir se a cota deve seguir `btm_settings.btm_unit` (camada moderna).

## EC-14 — Cota métrica em unidade não prevista 🟢
- **Cenário:** `length_unit = 'KILOMETERS'` ou `'MICROMETERS'`.
- **Comportamento legado:** cai em "outra métrica" → centímetros (3).
- **Impacto:** exibição inesperada, mas legível.
- **Mitigação:** aceitável; documentar.

## EC-15 — Estilo de anotação não atinge cotas 🟢
- **Cenário:** usuário muda tamanho do texto da cota e clica "Apply Settings to All".
- **Comportamento legado:** o filtro exige `obj.type == 'MESH'`, mas cotas são `CURVE`; além disso usa `Socket_3/4/5` fixos (`ops.py:171-184`).
- **Impacto:** nenhuma cota muda; o contador ainda reporta sucesso parcial.
- **Mitigação:** T-23.

## EC-16 — "Extend Line" da cena não propaga 🟢
- **Cenário:** alterar `annotation_dimension_extend_line`.
- **Comportamento legado:** o `update=` aponta para `update_dimension_tick_length`, que só reescreve `Tick Length` (`hb_props.py:707`, `:111`).
- **Impacto:** cotas existentes mantêm a linha de extensão antiga.
- **Mitigação:** callback próprio (T-13).

## EC-17 — `CabinetPartModifier` com token sem arquivo 🟢
- **Cenário:** `add_node('CPM_INEXISTENTE', ...)`.
- **Comportamento legado:** `get_node` retorna `None`; modificador `NODES` criado sem grupo (`hb_types.py:848-870`).
- **Impacto:** o primeiro `set_input` levanta `ValueError`; se ninguém escrever inputs, o modificador fica inerte e invisível ao usuário.
- **Mitigação:** falhar cedo em `add_node` com mensagem do arquivo ausente.

## EC-18 — `run_calc_fix_until_stable` com objetos criados/apagados entre passadas 🟡
- **Cenário:** um driver ou calculadora que dispara criação de peças.
- **Comportamento legado:** comparação de `dimensions` por `zip` na ordem de coleta (`hb_utils.py:267-297`).
- **Impacto:** pares desalinhados → falsa não convergência (−1) ou falsa convergência.
- **Mitigação:** comparar por nome (T-12).

## EC-19 — `run_calc_fix` e `frame_set` com outros add-ons 🟢
- **Cenário:** cena com handlers `frame_change_pre/post` de terceiros (ex.: animação).
- **Comportamento legado:** cada passada chama `frame_set(atual+1)` e volta.
- **Impacto:** handlers de terceiros rodam 2× por passada; custo O(passadas × objetos) em projetos grandes.
- **Mitigação:** medir; se possível substituir por `depsgraph.update()` + `update_tag()` direcionado.

## EC-20 — Obstáculo: cabeçalho selecionado 🟡
- **Cenário:** o enum abre no primeiro item, que é `HEADER_WALL` (id 0).
- **Comportamento legado:** o cabeçalho não é posicionável (`hb_props_obstacles.py:216-252`).
- **Impacto:** o botão de posicionar aparece inativo até o usuário escolher um item real.
- **Mitigação:** padrão no primeiro item real (`base+1`).

## EC-21 — Operadores de UI em modo background 🟢
- **Cenário:** `tests/blender_smoke.py` com `--background`.
- **Comportamento legado:** `create_camera`, `set_recommended_settings` e o modal de escala usam `context.window`/`context.screen`/`space_data`.
- **Impacto:** `AttributeError`/`poll` falso nos testes.
- **Mitigação:** `poll()` explícito checando área `VIEW_3D`; testes cobrem apenas as funções puras.

## EC-22 — Dados pessoais do cliente no `.blend` 🟢
- **Cenário:** arquivo de projeto enviado a terceiros (fornecedor, fórum).
- **Comportamento legado:** nome, endereço, telefone e e-mail ficam em `Scene.hb_project` sem aviso (`hb_project.py:30-136`).
- **Impacto:** exposição de dados pessoais (LGPD).
- **Mitigação:** operador "limpar dados do cliente" antes de exportar/compartilhar. 🟡
