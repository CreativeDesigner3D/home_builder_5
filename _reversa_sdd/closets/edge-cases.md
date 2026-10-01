# closets — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/closets/`.

---

## EC-01 — Vão livre abaixo do mínimo 🟢
- **Cenário:** starter de 60" com 3 vãos, dois travados em 29".
- **Comportamento legado:** o vão livre recebe 1" (mínimo do solver) e a soma não fecha com a largura total
  (`solver_closets.py:41`).
- **Impacto:** painéis sobrepostos ou starter maior que o declarado, sem aviso.
- **Mitigação:** aviso visível e destaque do vão (T-05).

## EC-02 — Todos os vãos travados 🟢
- **Cenário:** 4 vãos travados somando 70" num starter de 80".
- **Comportamento legado:** escala proporcional para fechar (`solver_closets.py:44-49`).
- **Impacto:** larguras "travadas" mudam — contraria a expectativa de trava.
- **Mitigação:** manter, mas avisar que a trava foi violada. 🟡

## EC-03 — Override de altura de vão perdido 🟢
- **Cenário:** um vão foi editado para a mesma altura que o starter tinha; depois o starter muda.
- **Comportamento legado:** a propagação compara com `hb_last_height`; um override igual ao valor antigo é tratado como
  "não sobrescrito" e acompanha o starter (`types_closets.py:469-487`).
- **Impacto:** o usuário perde um ajuste que coincidia com o padrão.
- **Mitigação:** flag explícita de override por vão. 🟡

## EC-04 — Nenhuma caixa de gaveta cabe 🟢
- **Cenário:** gaveta de 60 mm de abertura com Metabox.
- **Comportamento legado:** usa o menor tamanho do sistema mesmo sem caber (`drawer_boxes_closets.py:56-85`).
- **Impacto:** caixa invade a gaveta de baixo; pedido de ferragem errado.
- **Mitigação:** avisar e marcar a gaveta como inválida.

## EC-05 — Pilha de gavetas com todas travadas 🟢
- **Cenário:** 4 frentes travadas que somam mais que a abertura.
- **Comportamento legado:** escala todas (`types_closets.py:1813-1831`).
- **Impacto:** alturas "travadas" mudam.
- **Mitigação:** igual a EC-02. 🟡

## EC-06 — Vão largo demais para a prateleira 🟢
- **Cenário:** starter de 84" com vão único travado.
- **Comportamento legado:** o auto nº de vãos só limita a 42" na inserção (`types_closets.py:1749-1754`); vãos travados
  maiores não geram aviso.
- **Impacto:** prateleira de 15/18 mm acima de ~800–900 mm empena.
- **Mitigação:** vão máximo do preset com aviso. 🟡

## EC-07 — Grab travado após carregar arquivo 🟡
- **Cenário:** usuário abre outro `.blend` com o grab ativo.
- **Comportamento legado:** `_drag_op` global não é limpo e o `poll` exige `_drag_op is None` (`op_grab_closet.py:55-59, 386-391`).
- **Impacto:** grab não funciona mais até reiniciar o Blender.
- **Mitigação:** limpar em `load_post` (T-03).

## EC-08 — Exceção no modal de inserção 🟡
- **Cenário:** erro no `modal()` de `place_starter` ou `add_part`.
- **Comportamento legado:** sem `try/except`; o handler de cotas só é removido em cancel/finish (`ops_closet.py:1226-1330, 1744-1784`).
- **Impacto:** cotas fantasmas desenhadas na viewport.
- **Mitigação:** T-18.

## EC-09 — Desativar a extensão com Open Door ativo 🟢
- **Cenário:** desativar a extensão durante a animação de abrir portas.
- **Comportamento legado:** `unregister()` não remove o `event_timer` nem encerra o modal (`op_open_door_closet.py:92-100, 223-230`).
- **Impacto:** timer chamando código descarregado.
- **Mitigação:** T-03.

## EC-10 — Toggle de modo em background 🟢
- **Cenário:** script em `--background` muda `closet_selection_mode`.
- **Comportamento legado:** o callback chama `bpy.ops.hb_closets.toggle_mode` sem `try` (`props_closets.py:97-100`).
- **Impacto:** erro de contexto ao abrir/editar arquivos sem UI.
- **Mitigação:** chamar função direta (T-24).

## EC-11 — Desfazer abertura de porta 🟢
- **Cenário:** usuário abre portas no Open Door e aperta Ctrl+Z.
- **Comportamento legado:** `open_door_mode` grava `hb_door_open/hb_drawer_open` com `bl_options={'REGISTER'}` sem `UNDO`.
- **Impacto:** o undo desfaz outra coisa; portas ficam abertas no arquivo.
- **Mitigação:** T-24.

## EC-12 — Ilha dupla com frentes no lado de trás 🔴
- **Cenário:** ilha dupla com portas no lado BACK.
- **Comportamento legado:** o lado BACK não tem puxador nem portas de vão (`types_closets.py:914-915, 1037-1039`).
- **Impacto:** ilha inutilizável de um lado.
- **Mitigação:** T-17 (Q-05).

## EC-13 — Preset "Doors Open" sem portas abertas 🟡
- **Cenário:** aplicar `DOORS_OPEN_*`.
- **Comportamento legado:** o comentário diz que abre as portas, o código não (`types_closets.py:2142-2143` × `:2180-2186`).
- **Impacto:** nome confuso do preset.
- **Mitigação:** T-16.

## EC-14 — Linhas do grab invisíveis 🟢
- **Cenário:** Blender em Vulkan/Metal.
- **Comportamento legado:** `UNIFORM_COLOR` + `gpu.state.line_width_set(2/3)` (`op_grab_closet.py:273-301`); espessura > 1
  não é garantida.
- **Impacto:** guias finas ou invisíveis.
- **Mitigação:** `POLYLINE_UNIFORM_COLOR` (T-22).

## EC-15 — Objetos soltos na coleção da cena 🟢
- **Cenário:** apagar a coleção de um closet.
- **Comportamento legado:** puxadores, cabides e perfis de moldura ficam em `scene.collection` (`types_closets.py:1001`;
  `pulls_closets.py:221`; `molding_closets.py:482, 523`).
- **Impacto:** objetos órfãos espalhados.
- **Mitigação:** T-26.

## EC-16 — Pasta de cabides do usuário fora da extensão 🟡
- **Cenário:** add-on rodando a partir do repositório (desenvolvimento).
- **Comportamento legado:** `user_hangers_dir` monta o pacote com os 3 primeiros segmentos de `__package__`
  (`pulls_closets.py:61-72`).
- **Impacto:** `extension_path_user` recebe o pacote errado.
- **Mitigação:** T-27.

## EC-17 — Moldura desatualizada 🟢
- **Cenário:** mudar a altura de um vão depois de adicionar a moldura.
- **Comportamento legado:** a moldura não se regenera (`molding_closets.py:393-405`).
- **Impacto:** moldura flutuando ou atravessando.
- **Mitigação:** T-28 (Q-09).

## EC-18 — Prateleira fixa adicionada fora da retícula 🟢
- **Cenário:** digitar 400 mm no rótulo de uma prateleira fixa.
- **Comportamento legado:** prateleiras adicionadas no modal encaixam na retícula; a digitação no rótulo grava o valor
  livre (`gpu_overlay_closets.py:635-670`).
- **Impacto:** prateleira fora dos furos do sistema 32 mm.
- **Mitigação:** encaixar no furo mais próximo também na digitação, com opção de valor livre. 🟡

## EC-19 — Sem furação nem lista de corte 🔴
- **Cenário:** levar um closet para produção.
- **Comportamento legado:** o 32 mm é só retícula; não há furos nem lista de corte (`types_closets.py:624-625`).
- **Impacto:** o marceneiro refaz tudo em outro software.
- **Mitigação:** T-30, T-31 (Q-02, Q-03).

## EC-20 — Medidas americanas no roupeiro 🟢
- **Cenário:** preset BR com o closet legado.
- **Comportamento legado:** chapa 19,05 mm, profundidade 356 mm, varão a 305 mm da parede, puxador a 1143 mm, frente de
  gaveta 190,5 mm.
- **Impacto:** roupeiro raso demais para cabide frontal (BR: 550–600 mm) e chapa inexistente no mercado.
- **Mitigação:** preset BR (Q-01).
