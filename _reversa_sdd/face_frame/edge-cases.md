# face_frame — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/face_frame/`.

---

## EC-01 — Móvel fora do registro de classes perde o rodapé 🟢
- **Cenário:** cômoda, criado-mudo, window seat, hutch ou bookcase storage editada pela sidebar.
- **Comportamento legado:** `_wrap_cabinet` cai em `FaceFrameCabinet` quando o `CLASS_NAME` não está em
  `WRAP_CLASS_REGISTRY` (`types_face_frame.py:8636-8700`); a base responde `_has_toe_kick()` False e os kicks são
  zerados/removidos (`:1592-1619`).
- **Impacto:** o móvel muda de forma após qualquer edição.
- **Mitigação:** T-06 (registrar todas e testar o registro).

## EC-02 — Bays travados maiores que o gabinete 🟡
- **Cenário:** gabinete de 60" com dois bays travados de 30" e um terceiro destravado.
- **Comportamento legado:** `share = (disponível − Σ travados)/1` negativo, sem clamp (`types_face_frame.py:1641-1725`).
- **Impacto:** bay com largura negativa, moldura invertida.
- **Mitigação:** clamp em 0 + aviso (T-11, Q-04).

## EC-03 — Edição do usuário trava o item 🟢
- **Cenário:** usuário digita a largura de um bay e depois muda a largura total do gabinete.
- **Comportamento legado:** a edição ligou `unlock_width`; o bay mantém a largura e só os outros se ajustam
  (`props_hb_face_frame.py:4031-4098`).
- **Impacto:** esperado, mas surpreende quem não vê o cadeado.
- **Mitigação:** indicar visualmente o item travado na sidebar e nos rótulos. 🟡

## EC-04 — Altura da geladeira com dois valores 🟢
- **Cenário:** gabinete de geladeira criado com a cena em 69".
- **Comportamento legado:** `cab_props['refrigerator_opening_height'] = …` (escrita por chave) não altera a `bpy.props`
  desde o 5.0; ela fica no padrão 62" e o `back_bottom_inset` usa 69" (`types_face_frame.py:7335`).
- **Impacto:** costas e abertura desencontradas em 7".
- **Mitigação:** T-02, TM-01 (Q-07).

## EC-05 — Recálculo em cascata na exposição 🟡
- **Cenário:** inserir um gabinete ao lado de outros três.
- **Comportamento legado:** cada `setattr` de acabamento/scribe fora de `suspend_recalc` dispara um recálculo completo
  (`exposure.py:416-440`) — até ~9 por gabinete, mais os vizinhos.
- **Impacto:** inserção lenta em cozinhas grandes.
- **Mitigação:** T-08.

## EC-06 — Exceção escondida no dreno do recálculo 🟢
- **Cenário:** um gabinete enfileirado em `suspend_recalc` levanta erro no recálculo.
- **Comportamento legado:** `except Exception: pass` no dreno (`types_face_frame.py:103-106`).
- **Impacto:** gabinete não atualizado, sem mensagem.
- **Mitigação:** T-05 (relatar).

## EC-07 — Guardas de reentrância por `id()` 🟡
- **Cenário:** o Blender entrega uma instância Python diferente para o mesmo objeto durante o recálculo.
- **Comportamento legado:** `_RECALCULATING` usa `id(root)` (`types_face_frame.py:8765-8777`).
- **Impacto:** recursão não detectada → recálculo duplo ou loop.
- **Mitigação:** chave por `as_pointer()` ou nome (T-05).

## EC-08 — Malhas órfãs após muitos recálculos 🟡
- **Cenário:** arrastar fronteiras de bay por alguns segundos.
- **Comportamento legado:** frentes, pivôs, puxadores, splitters e backings apagados com `bpy.data.objects.remove` e
  recriados a cada recálculo (`types_face_frame.py:5785-5830`, `:5961-5972`); as malhas ficam até salvar/recarregar.
- **Impacto:** arquivo e memória crescendo; referências Python inválidas em operadores longos.
- **Mitigação:** T-09 (Q-08).

## EC-09 — Tamanho exibido diferente do construído 🟡
- **Cenário:** split com um membro removido e `splitter_widths` customizado; o usuário trava um filho.
- **Comportamento legado:** `_redistribute_split_node` usa largura uniforme e ignora overrides, remoções, remove_bottom e
  front_drop (`types_face_frame.py:1763`); o solver constrói certo, mas o valor "congelado" ao travar é o exibido.
- **Impacto:** ao travar, a abertura muda de tamanho.
- **Mitigação:** T-12.

## EC-10 — Mid rail removido em split vertical 🟢
- **Cenário:** remover o membro de um split V.
- **Comportamento legado:** o colapso para 3/32" só vale para eixo H (`solver_face_frame.py:3051-3062`).
- **Impacto:** remoção sem efeito visível no V.
- **Mitigação:** documentar na UI ou implementar o colapso em V. 🟡

## EC-11 — remove_bottom com vão inferior sem frente 🟢
- **Cenário:** geladeira (vão inferior APPLIANCE) com remove_bottom.
- **Comportamento legado:** o último splitter vira BOTTOM_RAIL com a largura do bottom rail (`solver_face_frame.py:3063-3074`).
- **Impacto:** esperado; em outros front types o rail some.
- **Mitigação:** manter. 🟢

## EC-12 — Tipo de canto desconhecido 🟢
- **Cenário:** arquivo com `corner_type` que não é PIE_CUT, DIAGONAL nem PIE_CUT_DRAWER.
- **Comportamento legado:** `NotImplementedError` no recálculo (`types_face_frame_corner.py:312`, `:981`).
- **Impacto:** gabinete trava toda edição.
- **Mitigação:** T-21 (tratar como NONE com aviso).

## EC-13 — Gabinete girado em relação à parede 🟡
- **Cenário:** gabinete a 90° numa parede (ex.: ponta de península).
- **Comportamento legado:** a exposição usa `cab_obj.location.x` no X local da parede (`exposure.py:142-286`).
- **Impacto:** lados detectados errados → acabamento e scribe errados.
- **Mitigação:** T-18 (Q-10).

## EC-14 — Fusão automática indesejada 🟢
- **Cenário:** inserir um base a 0,5" de outro com a mesma altura e profundidade.
- **Comportamento legado:** os dois viram um gabinete (`types_face_frame.py:9025-9080`; `ops_placement.py:928-960`).
- **Impacto:** o usuário queria dois gabinetes separados (ex.: módulos de fabricação distintos).
- **Mitigação:** tornar a fusão opcional na inserção (tecla ou preferência). 🟡

## EC-15 — Quebra de gabinete de canto 🟢
- **Cenário:** "Break" num gabinete pie-cut.
- **Comportamento legado:** cantos não quebram (`types_face_frame.py:9331-9400`).
- **Impacto:** comando sem efeito.
- **Mitigação:** desabilitar o comando (poll) em cantos.

## EC-16 — Porta de vaidade em bay estreito 🟢
- **Cenário:** vaidade de 24" com duas portas destravadas e uma porta VANITY_DOOR.
- **Comportamento legado:** a porta de vaidade fica 4" maior que a cota igual (`solver_face_frame.py:2813-2852`);
  num bay estreito, as outras podem ficar muito pequenas ou negativas.
- **Impacto:** frentes degeneradas.
- **Mitigação:** limitar o extra ao que cabe. 🟡

## EC-17 — Peça manual desalinhada 🟢
- **Cenário:** tornar editável um stile e depois mudar a altura do gabinete.
- **Comportamento legado:** `IS_MANUAL_PART` fica fora da reescrita (`types_face_frame.py:1998-2020`).
- **Impacto:** stile no tamanho antigo.
- **Mitigação:** marcar peças manuais desatualizadas e oferecer "reverter". 🟡

## EC-18 — Split preview aberto ao desativar a extensão 🟢
- **Cenário:** usuário desativa a extensão com o diálogo `split_opening` aberto.
- **Comportamento legado:** o handler de `split_preview` só é removido pelo operador; o `unregister()` não o remove
  (`split_preview.py:218-236`).
- **Impacto:** callback apontando para código descarregado → erro ou crash.
- **Mitigação:** T-04.

## EC-19 — Enum dinâmico por índice 🟢
- **Cenário:** o usuário cadastra uma cor nova que entra no meio da lista de stains.
- **Comportamento legado:** itens sem cache das strings e com índice posicional (`props_hb_face_frame.py:195-258`).
- **Impacto:** gabinetes passam a mostrar outra cor; rótulos podem corromper.
- **Mitigação:** T-03, TM-03.

## EC-20 — Rotação de parede torta e scribe 🟢
- **Cenário:** parede fora de esquadro, gabinete encostado.
- **Comportamento legado:** scribe automático fixo de 1/2" na parede e 1/4" no vizinho (`exposure.py:399-416`).
- **Impacto:** folga pode não bastar para paredes muito tortas.
- **Mitigação:** scribe configurável no preset. 🟡

## EC-21 — Lista de corte ausente 🔴
- **Cenário:** cozinha inteira em face frame.
- **Comportamento legado:** `cutting/` não lê as peças.
- **Impacto:** sem produção.
- **Mitigação:** T-34 (Q-05).

## EC-22 — Medidas americanas em projeto brasileiro 🟢
- **Cenário:** preset BR ativo com gabinete face frame.
- **Comportamento legado:** moldura 3/4", carcaça 1/2", costas 1/4", base 876 mm, bay máx. 36", catálogo CWP.
- **Impacto:** construção estranha ao marceneiro brasileiro e incompatível com chapas nacionais.
- **Mitigação:** decisão de permanência (Q-01) e catálogo isolado (Q-06).
