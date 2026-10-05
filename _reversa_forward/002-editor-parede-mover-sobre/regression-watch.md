# Regression watch — 002-editor-parede-mover-sobre

> Criado por `/reversa-coding` em 2026-10-05 (rodada 1: blocos B1 e B2; rodada 2: B3, B4, T036 e fechamento, W003–W004; pós-auditoria ao vivo: nenhum item novo no watch principal).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/ui/requirements.md#R-02` | O painel de propriedades (`BTM_PT_ObjectProperties`) mostra o objeto ativo de **todas** as bibliotecas (frameless, face frame, closets, módulo rápido, paredes e aberturas) com grupos por tipo; `BTM_PT_ContextProperties` não existe mais | redação | Spec regenerada descreve o painel de contexto só para objetos `btm_plane` ou volta a citar `BTM_PT_ContextProperties` |
| W002 | `_reversa_sdd/ui/requirements.md#R-02` (cotas) | Módulos de parede têm cotas editáveis (afastamento, anterior, posterior, inferior, superior) que movem o módulo mantendo as dimensões | presença | Spec não menciona cotas editáveis no painel de propriedades |
| W003 | `_reversa_sdd/soul.md` (lista de peças) + `cutting/part_sources.py` (rodada 2) | A lista de peças inclui, além dos módulos, a geometria livre marcada como peça de fabricação, com `source = "FREE_GEOMETRY"` e sem módulo (placa = 1 chapa, caixa = 6) | presença | Spec regenerada de `cutting` lista só as origens `CUTPART`/`SYNTHETIC` ou diz que a lista de peças vem apenas de módulos |
| W004 | `_reversa_sdd/ui/requirements.md#R-02` (rodada 2) | O painel de propriedades tem o grupo Geometria (medidas, fabricação, duplicar/espelhar/excluir) e, para paredes do HB5, editor, rebaixar, visibilidade e "Remover Parede…" | presença | Spec do painel de propriedades não cita geometria livre nem as operações de parede |

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso em cada `/reversa` futuro: data, veredito 🟢/🟡/🔴 por item. -->

## Arquivadas

<!-- Itens que deixaram de ser relevantes, com data e motivo. -->

## Observações

Itens sem peso de regressão (decisões novas desta feature, sem regra 🟢 de origem no legado):

- Botão direito do "3D View" com o modo "Mover Sobre" ligado inicia o arraste e não abre menu; desligado, volta ao
  menu do Blender (RN-10, D-14).
- Alinhamento no referencial de B com a frente em −Y para todas as bibliotecas; A assume a rotação de B e passa a
  filho da parede de B (D-16 + nota de execução). 🟡
- Tolerância de 12 px para os alvos (RN-06). 🟡
- Editor de Paredes 2D numa janela própria (Image Editor), rascunho em memória e aplicação no OK como um passo de
  desfazer; paredes removidas no editor deixam os módulos soltos (D-02, D-04, nota de execução). 🟡
- No OK do editor, pisos e tetos existentes são refeitos com o contorno novo (correção A005; antes era desvio). 🟡
- Rebaixar = parede com `hide_viewport` + filha `<parede>_Rebaixada` de 150 mm (`btm_wall_lowered`); invisível =
  `display_type = 'WIRE'` com `btm_display_prev` (D-19). 🟡
- Portas de ambiente com símbolo de abertura ganham folha 3D no primeiro "Abrir" (pivô `btm_room_door_pivot` + folha `btm_room_door_leaf`); janelas e vãos sem porta continuam sem "Abrir" (D-20, T016). 🟡
- Paredes da camada nova: contorno tracejado de referência; conversão sob pergunta ao abrir o editor, base Z ignorada (D-22). 🟡
- No OK do editor, módulos de trechos apagados: lista + "Remover os módulos junto?" (padrão não) (D-21). 🟢
- Medida real = face interna (tracejada); a externa = interna + espessuras; digitação direta na face/vértice (D-25, D-27). 🟢
- Salas legadas desenhadas no anti-horário (espessura para dentro) são lidas como estão; nelas a linha dos nós é a externa (D-25, limitação). 🟡
- Botão direito do "Mover Sobre" em todos os modos da viewport (19 mapas de modo + "3D View") (D-29). 🟡
- Desligar a extensão remove todos os operadores, menus e painéis (D-32; verificado pela fumaça por `bl_idname`). 🟢
- `_reversa_sdd/domain.md#R-03` (sentido do desenho define o lado da espessura; sem 🟢 na matriz de certeza): no Editor de Paredes o lado passa a ser a **Direção** do trecho e a sala fechada fica com a espessura para fora; o construtor "Desenhar Paredes" mantém a regra antiga. 🟡
- "Desenhar Paredes" 3D (legado): ímã de 15 px e pergunta "Deseja fechar a parede?" antes do `close_room` (antes: 0,15 m e fechava sem perguntar); tecla C fecha direto (D-39). 🟡
- Mudar `ceiling_height` atualiza a altura de todas as paredes de altura cheia (fora Mureta, meia-parede, parede falsa) (D-38). 🟢
- Editor: nenhum contorno com o fim no início é aplicado aberto (D-35). 🟢
