# hb_placement — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Cada caso: cenário, comportamento legado, impacto e mitigação. Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Caminhos relativos a `blendertomob/`.

---

## EC-01 — Cursor dentro de um obstáculo 🟡
- **Cenário:** o mouse passa sobre um gabinete já posicionado na mesma parede.
- **Comportamento legado:** a varredura faz `gap_start = x_end` do obstáculo, que fica à direita do cursor; o novo objeto encosta na borda direita do obstáculo (`hb_placement.py:1116-1139`).
- **Impacto:** o preview "pula" para a direita mesmo que haja espaço livre à esquerda mais perto.
- **Mitigação:** escolher o vão livre mais próximo do cursor (esquerda ou direita). Depende de Q-02.

## EC-02 — Obstáculos sobrepostos 🟡
- **Cenário:** um gabinete alto em `[0; 0,6]` e um filtro/obstáculo curto em `[0,2; 0,3]` (ex.: tomada filha da parede).
- **Comportamento legado:** a lista é ordenada por início; ao passar pelo curto, `gap_start = 0,3`, recuando em relação ao `0,6` do longo.
- **Impacto:** o objeto novo pode sobrepor o gabinete alto.
- **Mitigação:** mesclar intervalos antes da varredura (T-15).

## EC-03 — "Além do último" usa o fim do último por início 🟢
- **Cenário:** o último obstáculo por início é curto e está dentro de um anterior mais longo.
- **Comportamento legado:** o teste usa `children[-1][1]` e não o maior fim (`hb_placement.py:1127`).
- **Impacto:** mesmo efeito de EC-02 na ponta direita.
- **Mitigação:** usar `max(x_end)` (coberto pela mesclagem de T-15).

## EC-04 — Parede sem modificador GN 🟢
- **Cenário:** objeto marcado `IS_WALL_BP` sem modificador (arquivo corrompido ou importado).
- **Comportamento legado:** `find_placement_gap_by_side` retorna `(None, None, None)`.
- **Impacto:** consumidor que não checa `None` falha com `TypeError`.
- **Mitigação:** consumidores tratam `None` como "posicionamento livre".

## EC-05 — Filho sem `mod_name` 🟡
- **Cenário:** objeto comum (ex.: um cilindro) filho da parede.
- **Comportamento legado:** `get_input('Dim X')` falha, é engolido e o filho entra com largura 0 (`hb_placement.py:978-986`).
- **Impacto:** obstáculo pontual; gabinetes podem sobrepor o objeto.
- **Mitigação:** usar `obj.dimensions` (bounding box) como fallback.

## EC-06 — Objeto girado fora de 0°/±90°/180° 🟢
- **Cenário:** obstáculo girado 45° na parede.
- **Comportamento legado:** fora da tolerância de 0,1 rad cai no caso "outro" → `[x, x+DimX]` (`hb_placement.py:999-1017`).
- **Impacto:** extensão errada (não considera a projeção real).
- **Mitigação:** projetar os 4 cantos da pegada, como já é feito para ilhas.

## EC-07 — Lado da parede decidido só por `location.y` 🟢
- **Cenário:** filho com origem no meio da espessura (`y == t/2`) ou com profundidade que atravessa a parede.
- **Comportamento legado:** `y < t/2` → frente; `y == t/2` → trás (`hb_placement.py:972`).
- **Impacto:** objetos centralizados ficam do lado "trás" por arredondamento.
- **Mitigação:** usar o centro da pegada e uma tolerância; objetos que atravessam contam nos dois lados.

## EC-08 — Vão menor que a largura do objeto 🟢
- **Cenário:** vão de 0,4 m para um gabinete de 0,6 m.
- **Comportamento legado:** `snap_x = gap_start` (RN-18); o objeto sobrepõe o obstáculo seguinte sem aviso.
- **Impacto:** colisão silenciosa.
- **Mitigação:** sinalizar o conflito (cota vermelha) e/ou impedir a confirmação.

## EC-09 — Parede sem obstáculos não centraliza 🟢
- **Cenário:** parede vazia; cursor a 0,1 m da ponta, gabinete de 0,6 m.
- **Comportamento legado:** `snap_x = cursor_x` (RN-19), sem prender à borda; o gabinete pode passar da ponta da parede se o cursor estiver perto do fim.
- **Impacto:** gabinete "sai" da parede.
- **Mitigação:** aplicar a mesma regra de RN-18 também para a parede vazia (decidir paridade, Q-02).

## EC-10 — Vão estreito com recuos 🟢
- **Cenário:** vão de 1,5" (38 mm) com recuos de 1/2" nos dois lados.
- **Comportamento legado:** recuos escalados até restar 1" (`hb_placement.py:1263-1269`).
- **Impacto:** esperado; mas em projetos métricos o mínimo de 25,4 mm é arbitrário.
- **Mitigação:** tornar o mínimo configurável (T-18).

## EC-11 — Canto interno × canto externo com paredes quase paralelas 🟢
- **Cenário:** vizinha com ângulo de ~179,99°.
- **Comportamento legado:** produto escalar próximo de 0; limiar 1e-4 (`hb_placement.py:1143-1189`).
- **Impacto:** classificação instável → recuo aparece e some com pequenos movimentos.
- **Mitigação:** tratar |dot| < limiar como "reto" (sem recuo), explicitamente.

## EC-12 — Parede em T quase paralela 🟢
- **Cenário:** parede encostada com |y| < 0,001 na direção.
- **Comportamento legado:** ignorada como T (`hb_placement.py:868-915`).
- **Impacto:** parede paralela sobreposta não bloqueia.
- **Mitigação:** aceitável; documentar.

## EC-13 — Ilha girada perto da faixa de profundidade 🟢
- **Cenário:** ilha girada cuja pegada toca a faixa de 24" por um canto.
- **Comportamento legado:** vira obstáculo recortado; descartada se < 1/4" (`hb_placement.py:1028-1070`).
- **Impacto:** pequenas pontas de ilha podem bloquear um trecho estreito da parede.
- **Mitigação:** aceitável; a faixa deveria vir da profundidade real do objeto posicionado (já usa `object_depth` se informado).

## EC-14 — `hit_face_index == -1` ou índice de mesh original × avaliado 🟡
- **Cenário:** Ctrl sobre objeto com modificador GN.
- **Comportamento legado:** `snap_to_object` indexa `polygons[hit_face_index]` do mesh avaliado; −1 pega o último polígono (`hb_snap.py:131-145`).
- **Impacto:** snap a vértices de uma face errada.
- **Mitigação:** T-03; checar `>= 0` e `< len(polygons)`.

## EC-15 — Sem viewport 3D sob o mouse 🟢
- **Cenário:** mouse sai para o Outliner durante o modal.
- **Comportamento legado:** `get_region` retorna `None`; `update_snap` acessa `self.region.x` → `AttributeError` (`hb_placement.py:169-172`).
- **Impacto:** modal aborta com traceback, previews ficam na cena.
- **Mitigação:** T-01.

## EC-16 — Modal abortado pelo Blender 🟡
- **Cenário:** usuário abre outro arquivo (Ctrl+O) durante o posicionamento.
- **Comportamento legado:** nenhum mixin tem `cancel()`; handlers `_placement_dim_handle`/`_dim_draw_handle` ficam registrados.
- **Impacto:** erro a cada redesenho (referência a operador morto).
- **Mitigação:** T-20, T-22.

## EC-17 — `add_dimension_draw_handler` chamado duas vezes 🟢
- **Cenário:** consumidor reinicia a cota sem remover o handler.
- **Comportamento legado:** o primeiro handle é sobrescrito e nunca removido (`hb_placement.py:1400-1404`).
- **Impacto:** indicador de snap duplicado e vazamento.
- **Mitigação:** idempotência (T-20).

## EC-18 — Digitação de unidades e frações mistas 🟡
- **Cenário:** usuário quer digitar `2'6"` ou `60cm`.
- **Comportamento legado:** `NUMBER_KEYS` só aceita dígitos, `.`, `-`, `/`; aspas, espaço e letras não entram no buffer (`hb_placement.py:55-64`).
- **Impacto:** metade do parser nunca é exercida pela UI; frações mistas impossíveis.
- **Mitigação:** ampliar as teclas aceitas (T-09, Q-03).

## EC-19 — Divisão por zero no parser 🟢
- **Cenário:** buffer `1/0`.
- **Comportamento legado:** `ZeroDivisionError` capturado; retorna `None`.
- **Impacto:** o consumidor precisa checar `None` antes de aplicar.
- **Mitigação:** manter; testes de consumidor.

## EC-20 — Valor negativo digitado 🟢
- **Cenário:** `-50` como largura.
- **Comportamento legado:** `-` é tecla válida; o parser retorna −0,05 m sem validação.
- **Impacto:** largura negativa enviada ao gabinete.
- **Mitigação:** validar por alvo (largura/altura/profundidade > 0; offsets podem ser negativos).

## EC-21 — Custo por tick em cenas grandes 🟢
- **Cenário:** cozinha com centenas de peças.
- **Comportamento legado:** `view_layer.update()` + varredura de `scene.objects` para T e ilhas a cada `MOUSEMOVE`.
- **Impacto:** lentidão perceptível no posicionamento.
- **Mitigação:** cache por modal das paredes e gabinetes livres (T-14).

## EC-22 — Duplicação fora da VIEW_3D 🟡
- **Cenário:** `duplicate_object_hierarchy` chamado de um contexto sem área 3D.
- **Comportamento legado:** `bpy.ops.object.duplicate` falha no `poll`; o token `_HB_DUP_TOKEN` pode ficar nos originais.
- **Impacto:** cópia não criada e marcador residual.
- **Mitigação:** T-23; limpar o token em `finally`.

## EC-23 — Gabinete preso à parede como alvo de encosto 🟢
- **Cenário:** hit num gabinete filho de parede.
- **Comportamento legado:** `find_cabinet_bp` para ao encontrar `IS_WALL_BP` e retorna `None` (RN-24).
- **Impacto:** esperado — na parede o encaixe vem do vão, não do encosto.
- **Mitigação:** manter.
