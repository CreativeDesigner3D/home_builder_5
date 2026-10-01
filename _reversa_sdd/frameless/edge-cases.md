# frameless — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/frameless/`.

---

## EC-01 — Lista de tamanhos curta no splitter vertical 🟢
- **Cenário:** `SplitterVertical` com `splitter_qty = 2` e `opening_sizes = [0.15]`.
- **Comportamento legado:** o laço final acessa `self.opening_sizes[i-1]` para `i = 1..qty+1` sem checar o tamanho
  (`types_frameless.py:1020-1024`) → `IndexError`; o `SplitterHorizontal` checa (`:1135`).
- **Impacto:** criação do gabinete interrompida no meio, deixando objetos parciais na cena.
- **Mitigação:** completar a lista com 0 (igual) até `qty + 1` (T-13).

## EC-02 — Vãos fixos maiores que a altura útil 🟢
- **Cenário:** gaveta superior fixa de 6" + porta fixa de 30" num inferior com 30" úteis.
- **Comportamento legado:** a calculadora atribui `(total − Σ fixos)/n` sem proteção → vão igual negativo (`hb_props.py:294-330`).
- **Impacto:** abertura com altura negativa, frentes invertidas.
- **Mitigação:** clamp em 0 + aviso (decisão `hb_core` Q-09).

## EC-03 — Gabinete redimensionado depois de criado o splitter 🟢
- **Cenário:** inferior "Base Door Drw" de 34,5" alterado para 30".
- **Comportamento legado:** `total_distance` é driver, mas os prompts `Opening i Height` só mudam quando `calculate()`
  roda (`types_frameless.py:963`); os vãos iguais ficam com a altura antiga.
- **Impacto:** porta sobrando para fora da caixa até rodar a calculadora.
- **Mitigação:** T-14 (recalcular ao mudar `Dim Z`) — Q-06.

## EC-04 — Porta 5 peças pequena demais 🟢
- **Cenário:** estilo 5 peças com montantes de 2" aplicado a uma porta de 4,5".
- **Comportamento legado:** `assign_style_to_front` devolve a string "Front too narrow…" e não aplica o estilo
  (`props_hb_frameless.py:1088-1092`); quem chama em lote não mostra a mensagem.
- **Impacto:** porta lisa num projeto todo de 5 peças, sem aviso.
- **Mitigação:** `report` visível e mínimo unificado (T-34; `product_common` Q-05).

## EC-05 — Porta alta ganha travessa central automática 🟢
- **Cenário:** porta de 46" num estilo sem `add_mid_rail`.
- **Comportamento legado:** acima de 45,5" a travessa central é adicionada e entra no mínimo de altura
  (`props_hb_frameless.py:1083-1086`, `:1119-1130`).
- **Impacto:** esperado nos EUA; no Brasil a regra depende do fornecedor de portas.
- **Mitigação:** limiar no preset (Q-04). 🟡

## EC-06 — Trocar o tipo de rodapé depois de criado 🟡
- **Cenário:** inferior criado com rodapé 0 (laterais entalhadas) e o prompt muda para 3 (niveladores).
- **Comportamento legado:** `Toe Kick Type` é lido uma vez na criação (`types_frameless.py:144`); a geometria não muda.
- **Impacto:** prompt e geometria inconsistentes.
- **Mitigação:** T-10 (reconstruir) — Q-10.

## EC-07 — Espessura do gabinete alterada e frentes desalinhadas 🟢
- **Cenário:** `Material Thickness` de 3/4" para 18 mm num gabinete existente.
- **Comportamento legado:** `Left/Right/Top/Bottom Thickness` da abertura não são drivers do `Material Thickness`;
  só `update_material_thickness_prompts` os corrige (`types_frameless.py:1156-1169`; `ops_defaults.py:31-56`).
- **Impacto:** sobreposição calculada com a espessura antiga.
- **Mitigação:** T-18 (driver).

## EC-08 — Estilo removido troca o estilo de outros gabinetes 🟢
- **Cenário:** estilos 0, 1, 2; gabinetes usando 1 e 2; remove-se o estilo 1.
- **Comportamento legado:** quem usava 1 vai para 0; quem usava 2 é decrementado para 1 (`ops_styles.py:376-422`).
  Se o arquivo for aberto por outra versão com a coleção em ordem diferente, os vínculos trocam.
- **Impacto:** acabamentos trocados sem o usuário perceber.
- **Mitigação:** identificador estável (T-33, TM-01).

## EC-09 — Preview atingido pelo próprio raycast 🟢
- **Cenário:** mover o mouse devagar sobre o preview do `place_cabinet`.
- **Comportamento legado:** o preview do frameless não grava `HB_CURRENT_DRAW_OBJ` (face_frame e closets gravam);
  `hb_snap` pode acertar o próprio preview (`hb_snap.py:57,73`).
- **Impacto:** preview "pula" ou fica preso em si mesmo.
- **Mitigação:** T-29.

## EC-10 — Operador de inserção chamado sem INVOKE 🟡
- **Cenário:** script chama `bpy.ops.hb_frameless.place_cabinet()` (EXEC_DEFAULT).
- **Comportamento legado:** o modal começa em `execute()` e chama `modal_handler_add` sem evento de janela
  (`ops_placement.py:270-…`).
- **Impacto:** operador preso ou erro em `--background`.
- **Mitigação:** `invoke` explícito; `execute` cria sem modal (T-28).

## EC-11 — Vão livre menor que a largura mínima 🟢
- **Cenário:** 8" entre um alto e a parede, com preenchimento automático ligado.
- **Comportamento legado:** `qtd = ceil(8/36) = 1` e largura = 8" (`ops_placement.py:1057-1063`); não há mínimo.
- **Impacto:** gabinete de 8" — fora do padrão de fabricação.
- **Mitigação:** largura mínima no preset; abaixo disso, sugerir painel/filler (aviso de `hb_placement` Q-08). 🟡

## EC-12 — Canto próximo à ponta da parede 🟢
- **Cenário:** inserir "Pie Cut Corner" com o cursor a menos de uma largura do fim da parede.
- **Comportamento legado:** o canto encosta na ponta (direita com rotação −90°) (`ops_placement.py:1270-1307`).
- **Impacto:** esperado; mas numa parede sem vizinha à direita, o canto aponta para o vazio.
- **Mitigação:** só encostar se houver parede conectada nessa ponta. 🟡

## EC-13 — Cantos diagonais alto/aéreo 🟢
- **Cenário:** usuário insere "Diagonal Corner Tall".
- **Comportamento legado:** só a gaiola é criada; o inferior diagonal não tem portas (`types_frameless.py:2318-2324`).
- **Impacto:** gabinete vazio no projeto e na lista de corte.
- **Mitigação:** T-26 (Q-01).

## EC-14 — Cena de layout ativa ao criar gabinetes 🟡
- **Cenário:** template ou inserção rodando com uma cena de elevação ativa.
- **Comportamento legado:** padrões de medida vêm de `bpy.context.scene.hb_frameless` (cena corrente), estilos da cena
  principal (77 × 89 leituras).
- **Impacto:** gabinetes com medidas padrão de fábrica em vez das configuradas.
- **Mitigação:** T-05 (Q-09).

## EC-15 — Bancada depois de mudar a largura de um gabinete 🟢
- **Cenário:** bancada criada; um inferior passa de 600 para 800 mm.
- **Comportamento legado:** bancada é malha estática (`ops_countertop.py:235-482`); não acompanha.
- **Impacto:** bancada curta, recorte do fogão fora do lugar.
- **Mitigação:** T-39 (Q-05).

## EC-16 — Balanço lateral junto a alto adjacente 🟢
- **Cenário:** inferior a 6 mm de um alto.
- **Comportamento legado:** a supressão do balanço usa tolerância de ±5 mm (`ops_countertop.py:195-…`); a 6 mm o
  balanço de 1" é criado e invade o alto.
- **Impacto:** bancada colidindo com o alto.
- **Mitigação:** tolerância maior (ex.: ≤ espessura do balanço) ou checar interseção real. 🟡

## EC-17 — Crown em grupo com alturas desiguais 🟢
- **Cenário:** aéreo e alto lado a lado com topos desalinhados.
- **Comportamento legado:** o agrupamento exige topos alinhados; a moldura "morre" no vizinho não selecionado ou
  faz degrau UPPER→TALL (`ops_crown.py:342-1288`).
- **Impacto:** moldura interrompida.
- **Mitigação:** manter; expor o comportamento na UI. 🟢

## EC-18 — Lateral aplicada com espessura de frente diferente 🟢
- **Cenário:** frente de 18 mm em vez de 3/4".
- **Comportamento legado:** a profundidade `dim_y + 0,875"` está embutida na expressão do driver
  (`ops_cabinet.py:215-262`).
- **Impacto:** lateral 1,05 mm maior que o necessário.
- **Mitigação:** T-40.

## EC-19 — Template com quantidade que não cabe 🟡
- **Cenário:** template Geladeira/Fogão com 6 inferiores à esquerda numa parede curta.
- **Comportamento legado:** largura = área / quantidade, sem mínimo (`props_elevation_templates.py:566-775`).
- **Impacto:** gabinetes estreitíssimos ou de largura negativa se os eletrodomésticos excederem a parede.
- **Mitigação:** limitar a quantidade pela largura mínima e avisar.

## EC-20 — Enum de puxadores após apagar arquivo da biblioteca 🟢
- **Cenário:** o usuário apaga um `.blend` de `frameless_assets/cabinet_pulls` com o Blender aberto.
- **Comportamento legado:** o enum é varrido do disco a cada redraw; a seleção atual some e a string do item pode ser
  coletada (limitação de callbacks de enum) (`props_hb_frameless.py:108-134`).
- **Impacto:** texto corrompido na UI ou crash.
- **Mitigação:** T-04 (cache).

## EC-21 — Undo durante a pintura de estilos em lote 🟡
- **Cenário:** Ctrl+Z enquanto o timer modal aplica estilos.
- **Comportamento legado:** `_style` e `_cabinets` guardados entre ticks (`ops_styles.py:680-789`).
- **Impacto:** referências inválidas → exceção ou crash.
- **Mitigação:** T-36 (guardar nomes, revalidar a cada tick).

## EC-22 — Miniatura de grupo altera a cena 🟢
- **Cenário:** salvar um grupo na biblioteca do usuário.
- **Comportamento legado:** `film_transparent`, `use_freestyle` e `line_thickness` mudam e não são restaurados
  (`ops_library.py:278-307`).
- **Impacto:** próximos renders do usuário saem com fundo transparente/Freestyle.
- **Mitigação:** T-43.

## EC-23 — Linhas de snap acumulam materiais 🟢
- **Cenário:** criar 20 linhas de snap.
- **Comportamento legado:** `create_snap_line_mesh` cria um material novo por linha (`ops_snap_line.py:44-61`).
- **Impacto:** 20 materiais "Snap Line Material.0NN" no arquivo.
- **Mitigação:** T-44.

## EC-24 — Meia-parede com peças mal nomeadas 🟢
- **Cenário:** criar `HalfWall` e consultar a lista de peças.
- **Comportamento legado:** tampo e base nascem com o nome "Right End" (`types_products.py:527, 541`).
- **Impacto:** lista de corte/orçamento com nomes errados.
- **Mitigação:** corrigir os nomes (T-41).

## EC-25 — Medidas americanas em projeto métrico 🟢
- **Cenário:** projeto brasileiro com MDF 18 mm.
- **Comportamento legado:** chapa padrão 0,75" (19,05 mm), inferior 876 mm, profundidade 587 mm, aéreo a 1372 mm,
  overlay total 17,46 mm (`props_hb_frameless.py:1425-1698`).
- **Impacto:** projeto inteiro 1,05 mm por chapa fora do material real; lista de corte errada.
- **Mitigação:** preset BR (decisão `product_common` Q-06; T-01, T-20, T-30).

## EC-26 — Registro que falha em silêncio 🟢
- **Cenário:** erro de anotação numa propriedade do frameless.
- **Comportamento legado:** `register()` captura `Exception` e segue (`props_hb_frameless.py:2537-2558`).
- **Impacto:** `AttributeError: 'Scene' object has no attribute 'hb_frameless'` muito depois, longe da causa.
- **Mitigação:** T-02.

## EC-27 — Gabinete frameless fora da lista de corte 🔴
- **Cenário:** gerar lista de corte de uma cozinha montada com o frameless.
- **Comportamento legado:** `cutting/part_extractor.py` não lê os `CabinetPart` legados (lacuna L1 de `soul.md`).
- **Impacto:** o objetivo principal do produto (produção) não é atendido para esses gabinetes.
- **Mitigação:** T-47 (Q-08).
