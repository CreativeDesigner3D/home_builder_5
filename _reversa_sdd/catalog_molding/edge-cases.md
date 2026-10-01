# catalog_molding — Casos de Borda

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Cada caso traz: cenário, comportamento legado observado no código, impacto e mitigação recomendada.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

---

## EC-01 — Gabinete alterado depois das molduras 🟢
- **Cenário:** crown aplicada; um aéreo muda de 600 para 800 mm.
- **Comportamento legado:** nenhum handler de depsgraph; as molduras só mudam com "Refresh Molding" ou nova troca de
  pacote (`molding/ops.py:246-254`).
- **Impacto:** moldura curta ou atravessando o vizinho.
- **Mitigação:** marcar desatualizada (T-07, Q-04).

## EC-02 — Topos desalinhados por 2,5 cm 🟢
- **Cenário:** dois aéreos lado a lado com topos a 25 mm de diferença.
- **Comportamento legado:** a cota de alinhamento precisa coincidir em ±0,02 m (`engine.py:85-121`); viram duas corridas.
- **Impacto:** moldura interrompida com duas pontas.
- **Mitigação:** manter a tolerância, mas expor no painel quais gabinetes ficaram fora. 🟡

## EC-03 — Cadeia com ramificação 🟢
- **Cenário:** gabinetes em T (três vizinhos de um mesmo membro).
- **Comportamento legado:** membros não alcançados pela cadeia são anexados ao fim (`engine.py:124-152`).
- **Impacto:** sweep com salto (segmento atravessando o ar).
- **Mitigação:** dividir em várias cadeias. 🟡

## EC-04 — Eletrodoméstico suspenso no rodapé 🟢
- **Cenário:** forno de embutir a 800 mm do piso dentro de uma corrida de inferiores.
- **Comportamento legado:** bridges só incluem eletros com `z ≤ 0,02 m` (`adapters.py:55-66`); o forno é ignorado.
- **Impacto:** esperado. 🟢
- **Mitigação:** manter.

## EC-05 — Lateral de frameless encostada em parede não conectada 🟢
- **Cenário:** gabinete frameless a 4 cm de uma parede.
- **Comportamento legado:** a ponta é acabada se a sonda a 0,03 m para fora não cai em bbox de parede (tolerância 0,05)
  (`adapters.py:104-125`); a 4 cm cai dentro → não acabada.
- **Impacto:** sem retorno numa ponta visível.
- **Mitigação:** usar a exposição da unit (`face_frame/exposure.py`) também no frameless. 🟡

## EC-06 — Ilha com rotação não oposta 🟢
- **Cenário:** ilha com dois gabinetes a 0° e 90°.
- **Comportamento legado:** só é ilha com ≤ 2 rotações e, se duas, opostas (`engine.py:613-708`); senão vira corrida comum.
- **Impacto:** rodapé sem fechar o perímetro.
- **Mitigação:** aceitar ilhas em L. 🟡

## EC-07 — Sweep sem splines deixa curva órfã 🟢
- **Cenário:** cadeia toda de spans descartados.
- **Comportamento legado:** remove os objetos, não as curvas (`ops.py:174-177`).
- **Impacto:** curvas acumulando no arquivo.
- **Mitigação:** T-04.

## EC-08 — Nome de gabinete com vírgula 🟡
- **Cenário:** gabinete renomeado para "Base 60, pia".
- **Comportamento legado:** `HB_MOLDING_MEMBERS` guarda nomes separados por vírgula (`ops.py:14-16`).
- **Impacto:** membro mal identificado.
- **Mitigação:** T-04.

## EC-09 — Erro durante a troca de pacote 🟢
- **Cenário:** perfil de pack corrompido.
- **Comportamento legado:** `on_package_changed` captura e só faz `print` (`ops.py:300-307`).
- **Impacto:** usuário troca o pacote e nada acontece, sem mensagem.
- **Mitigação:** T-06.

## EC-10 — Três sistemas de moldura na mesma cozinha 🟢
- **Cenário:** crown pelo pacote da sala, mais "Assign Crown" do frameless e moldura do closet.
- **Comportamento legado:** implementações independentes criam objetos sobrepostos.
- **Impacto:** molduras duplicadas, lista de materiais errada.
- **Mitigação:** T-09 (Q-02).

## EC-11 — Closets sem moldura de sala 🔴
- **Cenário:** cômodo com roupeiros e o pacote de crown ligado.
- **Comportamento legado:** não há adaptador de closets (`adapters.py:16-52`).
- **Impacto:** roupeiro sem crown, diferente dos gabinetes vizinhos.
- **Mitigação:** T-02 (Q-03).

## EC-12 — Catálogo reativado quebra o painel 🟢
- **Cenário:** registrar `catalog/` e selecionar um item.
- **Comportamento legado:** o painel chama `hb_catalog.render_thumbnail`, inexistente (`ui_catalog.py:275-280`).
- **Impacto:** erro no `draw()`; painel em branco.
- **Mitigação:** T-13.

## EC-13 — Estilo aplicado ao objeto errado pelo catálogo 🟡
- **Cenário:** colocar um produto pelo catálogo com outro gabinete ativo.
- **Comportamento legado:** `_apply_global_assembly_config(context.active_object)` roda logo após abrir o modal
  (`ops_catalog.py:16-86`).
- **Impacto:** o gabinete anterior recebe o estilo.
- **Mitigação:** T-12.

## EC-14 — Timer do catálogo após `unregister` 🟢
- **Cenário:** desativar a extensão com sync pendente.
- **Comportamento legado:** o timer não é cancelado (`props_catalog.py:148-154`) e acessa `scene.hb_catalog` inexistente.
- **Impacto:** exceção no console.
- **Mitigação:** T-14.

## EC-15 — Miniaturas em pasta somente leitura 🟢
- **Cenário:** extensão instalada em diretório do sistema.
- **Comportamento legado:** grava em `catalog/thumbnails/` (`render_thumbnails.py:36-37`).
- **Impacto:** falha ao gravar; atualizações apagam as miniaturas.
- **Mitigação:** T-13.

## EC-16 — Contornos embutidos em polegadas 🟢
- **Cenário:** preset BR.
- **Comportamento legado:** `crown_simple` 0,875 × 3", `base_simple` 0,625 × 3" (`packages.py:183-216`); reveal 0,625".
- **Impacto:** perfis sem correspondência nos catálogos nacionais.
- **Mitigação:** pacotes BR (Q-05).
