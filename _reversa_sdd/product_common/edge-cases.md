# product_common — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

---

## EC-01 — Mid rail fixo acima do campo útil 🟢
- **Cenário:** `add_mid_rail=True`, `center_mid_rail=False`, `mid_rail_location = 12"` numa porta de 14" de altura.
- **Comportamento legado:** `mz = (0, max(mid_rail_location, brw))` não tem teto; a linha de painel superior fica com
  altura `H − trw − mz − mrw < 0` (`product_libraries/common/door_builder.py:180-190`). `build_door_mesh` pula a
  peça com altura ≤ 0 (`:1303-1304`), mas o mid rail sobrepõe a travessa superior.
- **Impacto:** porta com membros sobrepostos e sem painel superior, sem aviso. `layout_min_size` não pega o caso
  porque só soma larguras.
- **Mitigação:** limitar `mz` a `H − trw − mrw` (ou incluir `mid_rail_location` no mínimo) e avisar. 🟡

## EC-02 — Porta exatamente no tamanho mínimo 🟢
- **Cenário:** coifa com baia de largura igual a `min_w` de `layout_min_size`.
- **Comportamento legado:** a coifa compara com `≤` e troca por SLAB (`wood_hoods.py:729-731`); o painel teria
  1/2" de largura.
- **Impacto:** portas na fronteira viram SLAB; mudar 1 mm muda o estilo visível.
- **Mitigação:** manter para paridade; documentar o limiar na UI. 🟢

## EC-03 — Mínimos divergentes entre coifa e frente de armário 🟢
- **Cenário:** porta de 7" com membros de 3" (mínimo +1/2" = 6,5"; mínimo do face frame +1" = 7").
- **Comportamento legado:** na coifa sai porta de 5 peças; como frente de armário do face frame sai SLAB
  (`face_frame/props_hb_face_frame.py:3406-3423`).
- **Impacto:** mesmo estilo gera portas diferentes no mesmo projeto.
- **Mitigação:** unificar o limiar numa constante (decisão em Q-05).

## EC-04 — Overrides por lado zerados em portas espelhadas 🟢
- **Cenário:** par de portas com `right_stile_width = 0.0` numa e `left_stile_width = 0.0` na outra.
- **Comportamento legado:** o piso é 0.0 (não 1/2"); o membro de largura zero é pulado na malha
  (`door_builder.py:52-55`, `:1303-1304`).
- **Impacto:** esperado — as portas se encostam sem montante duplo. Se o usuário digitar um override entre 0 e 1/2",
  o membro fica mais fino que o piso uniforme, sem limite.
- **Mitigação:** aceitar 0 como "sem membro" e aplicar piso de 1/2" a valores > 0. 🟡

## EC-05 — Mid stiles demais para a largura 🟢
- **Cenário:** `mid_stile_count = 6` numa porta de 12" com montantes de 3".
- **Comportamento legado:** a largura de coluna `(W − (lsw + rsw + m·msw))/(m+1)` fica negativa; os painéis são
  pulados; os mid stiles são emitidos e se sobrepõem (`door_builder.py:193-207`). O mínimo (`layout_min_size`) já
  indicaria SLAB, mas só a coifa consulta o mínimo.
- **Impacto:** geometria sobreposta se o consumidor não checar o mínimo.
- **Mitigação:** `build_door_mesh` deve checar `layout_min_size` e cair para SLAB por conta própria.

## EC-06 — Espessura da porta menor que a região moldada do perfil 🟢
- **Cenário:** perfil externo desenhado para 3/4" aplicado numa porta de 5/8".
- **Comportamento legado:** como não há trecho reto a esticar, todo o eixo v é escalado
  (`door_profiles.py:598-610`).
- **Impacto:** o perfil fica achatado (a forma do cortador muda).
- **Mitigação:** aceitar; opcionalmente avisar quando a escala for < 1. 🟢

## EC-07 — Painel raised mais largo que a célula 🟢
- **Cenário:** painel com `field_u = 2"` numa célula de 3,5".
- **Comportamento legado:** `min(w, h) ≤ 2·field_u` → `_emit_raised_panel` devolve `False` e o painel vira caixa
  plana (`door_builder.py:460-466`).
- **Impacto:** portas estreitas perdem o raise sem aviso — coerente com a marcenaria, mas invisível ao usuário.
- **Mitigação:** manter; registrar o fallback para exibição de diagnóstico. 🟡

## EC-08 — Profundidade da ranhura maior ou igual à espessura do painel 🟢
- **Cenário:** BEAD (0,11") num painel de 1/8".
- **Comportamento legado:** nenhuma ranhura é gerada (`door_builder.py:497-571`).
- **Impacto:** estilo beadboard aparece liso.
- **Mitigação:** manter para não atravessar o painel. 🟢

## EC-09 — Padrão de mullion inválido para o tamanho do vidro 🟢
- **Cenário:** MISSION num vidro de 5" de largura com barra de 7/8" (limite `w ≤ 3·bw + 3"` = 5,625").
- **Comportamento legado:** `_mullion_layout` devolve `[]`; o vidro fica sem barras (`door_builder.py:713-766`).
- **Impacto:** estilo pedido não aparece, sem mensagem.
- **Mitigação:** manter; expor "padrão não cabe" na UI de estilo. 🟡

## EC-10 — Célula arqueada estreita 🟢
- **Cenário:** porta Twin com vidros de 1,8".
- **Comportamento legado:** célula ≤ 2" desliga o arco (`face_frame/props_hb_face_frame.py:3523-3526`); a
  travessa continua alargada pelo rise calculado pelo consumidor.
- **Impacto:** travessa larga sem arco. 🟡
- **Mitigação:** só alargar a travessa quando o arco for efetivamente emitido.

## EC-11 — Perfil `.blend` editado no mesmo segundo 🟡
- **Cenário:** o usuário salva o `.blend` do perfil duas vezes num intervalo menor que a resolução de `mtime`.
- **Comportamento legado:** a chave `(path, mtime, res)` não muda e o cache devolve a versão antiga
  (`door_profiles.py:101-103`).
- **Impacto:** edição ao vivo do perfil não aparece até a próxima gravação.
- **Mitigação:** incluir o tamanho do arquivo na chave ou oferecer "recarregar perfis". 🟡

## EC-12 — Datablocks órfãos após carregar perfil 🟡
- **Cenário:** o `.blend` do perfil traz materiais ou curvas com outros usuários.
- **Comportamento legado:** o `finally` remove objetos e curvas órfãs; materiais trazidos junto não são removidos
  (`door_profiles.py:105-126`).
- **Impacto:** materiais `.001` acumulando no arquivo do usuário.
- **Mitigação:** T-16 (carregar só curvas ou limpar também materiais sem usuário).

## EC-13 — Nome de borda de catálogo sem builder 🟢
- **Cenário:** estilo com borda "Estate" ou "Eclipse".
- **Comportamento legado:** `named_edge_section` devolve `None` → borda reta (`door_profiles.py:658-677`).
- **Impacto:** a porta renderizada não corresponde ao catálogo, sem aviso.
- **Mitigação:** registrar os nomes sem builder e avisar ao aplicar o estilo. 🟡

## EC-14 — Propriedades de texto de coifa e pia 🟢
- **Cenário:** `Hood().create(...)` e `Sink().create(...)`.
- **Comportamento legado:** `add_property(..., 'TEXT', ...)` não tem ramo para `'TEXT'`; "Hood Style" e "Sink Type"
  nunca são criadas (`types_appliances.py:176`, `:192`; `hb_props.py:335-374`).
- **Impacto:** qualquer leitura dessas chaves devolve o padrão ou levanta `KeyError`.
- **Mitigação:** T-21 (decisão em Q-08).

## EC-15 — Micro-ondas over-range não volta ao padrão 🟢
- **Cenário:** o usuário marca e depois desmarca "Over Range".
- **Comportamento legado:** `set_over_range()` não recebe parâmetro e só fixa 30×17×16"; não existe caminho de
  volta para 24×12×14" (`types_appliances.py:156-161`). Os outros toggles (`set_double_oven`,
  `set_counter_depth`) recebem booleano.
- **Impacto:** dimensões presas no over-range.
- **Mitigação:** `set_over_range(on=True)` simétrico aos demais. 🟢

## EC-16 — Diálogo de prompts reconstrói a coifa a cada alteração 🟢
- **Cenário:** o usuário mexe em vários campos do `blendertomob.wood_hood_prompts` e fecha o diálogo sem confirmar.
- **Comportamento legado:** `check()` chama `_apply()` e reconstrói a coifa a cada mudança
  (`wood_hoods.py:2059-2061`); não há rollback se o diálogo for cancelado.
- **Impacto:** alterações "canceladas" ficam aplicadas; sem passo de undo próprio para o cancelamento. 🟡
  Em coifas CUSTOM complexas, cada tecla dispara uma reconstrução completa (lentidão).
- **Mitigação:** guardar o estado em `invoke` e restaurar em `cancel()`; ou aplicar só em `execute`, com preview leve.

## EC-17 — Estilos inclinados não acompanham o cage 🟢
- **Cenário:** coifa TRADITIONAL redimensionada pelo gizmo/`Dim X` fora do diálogo.
- **Comportamento legado:** as peças são malha estática; só o diálogo reconstrói (`wood_hoods.py:279-310`).
- **Impacto:** coifa desalinhada do cage até nova reconstrução.
- **Mitigação:** reconstruir em handler de depsgraph com guarda de reentrância, ou marcar "precisa atualizar".

## EC-18 — Troca de estilo com peças manuais 🟢
- **Cenário:** peça tornada editável num MANTLE e estilo trocado para CHIMNEY.
- **Comportamento legado:** `_clear_hood_parts` preserva `IS_MANUAL_PART` (`wood_hoods.py:82-88`); a peça antiga
  convive com as novas.
- **Impacto:** peça órfã do estilo anterior, possivelmente sobreposta.
- **Mitigação:** avisar que há peças manuais antes da troca e oferecer revertê-las ou apagá-las. 🟡

## EC-19 — Restore apaga todos os modificadores da peça 🟢
- **Cenário:** o usuário tornou a peça editável e adicionou um modificador Bevel; depois usa "Revert to Parametric".
- **Comportamento legado:** `hood_part.modifiers.clear()` antes de recriar o modificador GN; drivers também são
  todos removidos (`wood_hoods.py:1709-1714`).
- **Impacto:** perda silenciosa de modificadores adicionados pelo usuário.
- **Mitigação:** remover só os modificadores que o snapshot conhece; avisar antes de reverter. 🟡

## EC-20 — Restore com datablocks renomeados ou inputs que falham 🟢
- **Cenário:** material referenciado no snapshot foi renomeado; um input não existe mais no node group.
- **Comportamento legado:** `_deser_value` devolve `None` para o material (`wood_hoods.py:1622-1632`); falhas de
  `set_gn_input` e de `driver_add` são ignoradas com `except … : pass/continue` (`:1719-1723`, `:1741-1748`).
  O restore devolve `True` mesmo assim.
- **Impacto:** peça "restaurada" sem material ou sem parte dos drivers, reportada como sucesso.
- **Mitigação:** contar falhas e reportar `WARNING` quando houver perda parcial.

## EC-21 — Variáveis de driver re-apontadas sempre para o cage 🟢
- **Cenário:** um driver da peça usava variável de outro objeto (não o cage).
- **Comportamento legado:** toda variável recebe `targets[0].id = hood_root` (`wood_hoods.py:1749-1754`); o comentário
  assume que todas apontam para o cage.
- **Impacto:** se a premissa quebrar (ex.: peça dependente de outra peça), o driver lê o objeto errado sem erro.
- **Mitigação:** gravar o nome do alvo no snapshot e só re-apontar quando o alvo original for o cage. 🟡

## EC-22 — Snapshot salvo no 5.1 e restaurado no 5.2 🟡
- **Cenário:** projeto antigo com `HOOD_PARAMETRIC_SNAPSHOT` em formato `modifiers["M"]["Socket_2"]`.
- **Comportamento legado:** `_migrate_mod_input_path` converte para `.properties.inputs.Socket_2.value`
  (`wood_hoods.py:46-54`); a viabilidade de `driver_add` nesse caminho no 5.2 não foi verificada.
- **Impacto:** se o caminho não for aceito, o `driver_add` falha em silêncio (EC-20).
- **Mitigação:** TT-09 e Q-04.

## EC-23 — Coifa sem o face frame carregado 🟢
- **Cenário:** registro do face frame falhou ou o módulo foi removido.
- **Comportamento legado:** imports tardios em `try/except Exception` devolvem `None`; a sobreposição cai para 1/2" e
  o acabamento não é aplicado (`wood_hoods.py:430-475`, `:1594-1601`).
- **Impacto:** coifa construída, mas com materiais padrão e sobreposição genérica, sem aviso.
- **Mitigação:** manter a tolerância; emitir um aviso uma vez por sessão. 🟡

## EC-24 — CUSTOM com opções de versão antiga 🟢
- **Cenário:** `WOOD_HOOD_CUSTOM_OPTS` salvo antes da divisão de `panel_rail_width`, ou sem chaves novas.
- **Comportamento legado:** `_get_custom_opts` mescla sobre `_CUSTOM_DEFAULTS` e migra `panel_rail_width` para
  topo/base quando estes faltam (`wood_hoods.py:489-506`); chaves desconhecidas são ignoradas.
- **Impacto:** abre sem erro. 🟢
- **Mitigação:** manter a mescla; TM-01.

## EC-25 — Provider de acessórios que falha no meio da iteração 🟢
- **Cenário:** o provider de um host levanta exceção depois de devolver alguns itens.
- **Comportamento legado:** `get_items` usa `list(fn())` e devolve `[]`; `all_items` já anexou os itens anteriores e
  mantém a lista parcial (`accessory_registry.py:28-54`).
- **Impacto:** `get_items` e `all_items` discordam para o mesmo host.
- **Mitigação:** em `all_items`, materializar `list(fn())` antes de anexar. 🟢

## EC-26 — Código de acessório repetido entre hosts 🟢
- **Cenário:** dois providers devolvem o mesmo `code`.
- **Comportamento legado:** `find(code)` devolve o primeiro na ordem de registro; o docstring assume unicidade
  (`accessory_registry.py:67-73`). Cada chamada de `find` reexecuta todos os providers.
- **Impacto:** item errado sem aviso; custo proporcional ao catálogo inteiro por consulta.
- **Mitigação:** índice por código com detecção de duplicata no registro. 🟡

## EC-27 — Medidas americanas em projeto brasileiro 🟢
- **Cenário:** projeto em mm com MDF 18 mm.
- **Comportamento legado:** coifa com chapa fixa de 3/4" (19,05 mm) e eletrodomésticos em tamanhos dos EUA
  (fogão 30" = 762 mm, geladeira 36"×70") (`wood_hoods.py:39`; `types_appliances.py`).
- **Impacto:** peças de 19,05 mm divergem da chapa real; eletrodomésticos fora dos padrões nacionais.
- **Mitigação:** parametrizar espessura e catálogo de eletrodomésticos (decisão em Q-06).
