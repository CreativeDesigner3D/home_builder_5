# Auditoria cruzada — 002-editor-parede-mover-sobre (4ª rodada: fechamento da sala e pé-direito)

> Data: 2026-10-05 · Gerado por `/reversa-audit` (somente leitor; esta é a única escrita).
> Artefatos analisados: [requirements.md](../requirements.md) · [roadmap.md](../roadmap.md) · [actions.md](../actions.md)
> (73 ações, todas `[X]`).
>
> **Pedido do titular:**
> - Ímã no ponto inicial: chegando bem perto, o editor pergunta "Deseja fechar a parede?" e, com Sim, liga os pontos.
> - Todas as paredes com o mesmo pé-direito das configurações.
> - Evidência: imagem de uma sala de 4 paredes com a última **solta no canto de origem**, sem encontro com a primeira.
>
> **Reprodução:** fumaça em `--background` com o modal do editor e eventos simulados no nível do operador (roteiro
> `close_typed.py` no scratchpad da sessão).

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 4 |
| MEDIUM | 1 |
| LOW | 1 |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|---|---|---|---|---|
| A001 | HIGH | Comportamento × requisito | **Fechar a sala digitando não fecha.** Lápis: 3000 Enter, 2000 Enter, 3000 Enter, 2000 Enter, voltando exatamente ao início. O último vértice cai em cima do primeiro, mas a cadeia **continua aberta** com um vértice duplicado: nós `(0,0) (3,0) (3,2) (0,2) (0,0)`, `fechada=False`, sem pergunta. No OK saem 4 paredes sem encontro no canto de origem, o defeito da imagem. A pergunta de fechamento só existe no caminho do **clique** | `walls2d/ops_editor.py` `_handle_draw` (ramo Enter → `_append`, sem teste de fechamento) · RN-17, RF-03 |
| A002 | HIGH | Cobertura (pedido novo) | **Não há ímã no ponto inicial.** A pré-visualização só trava na ortogonal e na grade (`preview_point`). A pergunta só aparece se o clique cair a até 12 px do início (`CLOSE_HIT_PX`). Um clique a 15 px (≈ 11 cm na escala do teste) cria um vértice solto, sem pergunta. RN-17 fala em "clicar de volta no ponto inicial" e não define ímã, raio nem o que acontece quando o ponto chega perto pelo teclado | `walls2d/ops_editor.py:26`, `preview_point`, `_handle_draw` · `requirements.md` RN-17 |
| A003 | HIGH | Requisito × pedido do titular | **Pé-direito das paredes novas não segue as configurações.** O lápis usa `new_height` com padrão fixo de 2,60 m (RN-18: "padrão 2.600"). O projeto define `scene.home_builder.ceiling_height` (2,4384 m no teste), que o construtor legado usa (`operators/walls.py:1604`) e que as cotas usam como pé-direito. Uma sala desenhada no editor nasce com altura diferente das demais | `walls2d/props.py` `new_height` · `requirements.md` RN-18 · `operators/walls.py:1604` |
| A004 | HIGH | Robustez do aplicador | **O OK aceita cadeia aberta cujo fim coincide com o início.** `apply.apply_plan` cria as paredes sem fechar o laço, sem `connect_to_wall` da última com a primeira e sem esquadria no canto. Nenhuma validação nem aviso no OK. É a rede de segurança que faltou para A001/A002 | `walls2d/apply.py` `apply_plan`; `model.Chain` (sem normalização de ponta duplicada) |
| A005 | MEDIUM | Requisito × pedido | "Todas as paredes com o mesmo pé-direito" não está definido para **paredes existentes** com alturas diferentes nem para Mureta (1.100 mm, RN-18) e para pé-direito final diferente do inicial. É preciso decidir se o OK uniformiza, só sugere ou só vale para paredes novas | `requirements.md` RN-18, RF-05 |
| A006 | LOW | Usabilidade | O raio de fechamento é fixo em pixels (12 px). Com a vista afastada, isso dá vários centímetros; aproximada, pede um clique muito preciso. Não há indicação visual de que o cursor está "no ímã" | `walls2d/ops_editor.py` `CLOSE_HIT_PX` |

## Impacto e direção (HIGH)

### A001 — fechar digitando deixa a sala aberta

**Reprodução**
1. Editor de Paredes, ferramenta **Construir Parede**.
2. Clique no ponto inicial.
3. Digite 3000 Enter, 2000 Enter, 3000 Enter, 2000 Enter: o desenho volta ao início.
4. OK.

**Resultado:** as paredes ficam com a última solta no canto (a imagem do titular).

**Direção:** quando um trecho termina a até X mm do ponto inicial (pelo teclado ou pelo clique), perguntar "Deseja fechar a parede?". Com Sim, juntar o ponto e fechar o contorno. **Via:** `/reversa-clarify` para fixar a regra, depois ação nova + `/reversa-coding`.

### A002 — ímã no ponto inicial

**Reprodução:** desenhe três trechos e clique a ~15 px do ponto inicial. Nasce um quarto vértice solto, sem pergunta.

**Direção:** a pré-visualização deve grudar no ponto inicial dentro de um raio (com destaque visual), e o clique ou Enter nesse estado deve perguntar. Falta definir o raio (em pixels de tela ou em mm). **Via:** `/reversa-clarify`.

### A003 — pé-direito diferente das configurações

**Reprodução**
1. Em Configurações, o pé-direito do projeto está em 2,44 m.
2. Desenhe uma sala no editor e dê OK.
3. As paredes saem com 2,60 m.

**Direção:**
- o padrão das paredes novas passa a ser `scene.home_builder.ceiling_height` (cena principal), em vez de 2,60 m;
- RN-18 precisa ser reescrita;
- é preciso decidir o que vale para paredes existentes (A005).

**Via:** `/reversa-clarify`.

### A004 — OK sem validação de laço

**Reprodução:** qualquer cadeia aberta cujo último vértice coincida com o primeiro (A001, ou arrastando o último vértice até o início).

**Direção:** no OK (ou ao terminar o desenho), detectar ponta coincidente (tolerância de 0,01 m, a mesma da leitura) e fechar o contorno, ou recusar com aviso. **Via:** ação nova + `/reversa-coding`.

## Itens verificados que passaram

**Fechamento pelo clique**
- Clicando a até 12 px do ponto inicial com 2 ou mais trechos, aparece a pergunta. "Sim" fecha o contorno com 4 trechos e escolhe a Direção para fora (fumaça e teste de interface com eventos reais).

**Consistência dos documentos**
- 73 ações, nenhuma aberta. Sem dependência fantasma, sem ciclo, sem RF/RN fantasma.
- Pares `[//]` com o mesmo arquivo continuam só T038/T053 e T039/T052 (já registrados).

**Coerência com o legado**
- O construtor legado usa `ceiling_height` para paredes de altura cheia (`operators/walls.py:1604`).
- As cotas da 002 também usam `ceiling_height` (`measure/scene_cotas.ceiling_height`).
- Só o lápis do editor diverge (A003).

**Ainda não verificado ao vivo:** a imagem foi atribuída ao fechamento digitado (A001), que reproduz o mesmo defeito. Também é possível que tenha sido feita pelo "Desenhar Paredes" do legado. Os achados valem para o editor de qualquer forma.
