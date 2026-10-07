# Regression watch — 003-modulos-agregados-reposicionar

> Criado por `/reversa-coding` em 2026-10-07 (rodada única, T001–T071).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-44) | A biblioteca do usuário tem, além dos grupos de gabinetes em `cabinet_groups/`, os módulos salvos de qualquer biblioteca em `modules/<categoria>/` com manifesto JSON (estilos, materiais e puxadores por nome) | presença | Spec regenerada descreve só os grupos de gabinetes frameless/face frame |
| W002 | `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-04) | Sem objeto sob o mouse, o ponto cai no plano de inserção ativo (`WindowManager.btm_insertion_plane`); sem plano, em Z = 0 | redação | Spec regenerada diz que o fallback é sempre o plano Z = 0 |
| W003 | `cutting/json_exporter.py` (contrato do JSON de produção) | `schema_version` 2.1.0; cada peça tem `machining` (lista, vazia sem agregado com furo real); o leitor aceita 2.0.0 | presença | Spec de `cutting` volta a 2.0.0 ou não cita `machining` |
| W004 | `_reversa_forward/001-addon-moveis-planejados/roadmap.md` (D-20) | O limite de 90° vale para módulos; folhas convertidas (`aggregate_leaf`) usam o máximo próprio, até 180° | redação | Spec de inspeção diz que toda frente é limitada a 90° sem exceção |
| W005 | `_reversa_sdd/frameless/requirements.md#Requisitos Funcionais` (RF-09, RF-20) e recálculos de face frame/closets | Troca de vão, estilo de gabinete e recálculo terminam reaplicando `btm_custom` do módulo (estilo, puxador e material por vão; material por grupo/peça) | presença | Spec regenerada não menciona a reaplicação, ou a personalização some depois de recalcular |
| W006 | `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-29) | O vínculo de estilo por índice continua para módulos sem personalização; módulos personalizados resolvem o estilo pelo nome | presença | Spec regenerada diz que todo estilo é por nome, ou que o índice foi removido |

## Histórico de re-extrações

<!-- Preenchido pelo agente reverso em cada `/reversa` futuro: data, veredito 🟢/🟡/🔴 por item. -->

## Arquivadas

<!-- Itens que deixaram de ser relevantes, com data e motivo. -->

## Observações

Itens sem peso de regressão (origem 🟡/🔴 ou decisão nova desta feature):

- Gavetas internas do frameless (`_add_rollouts_to_section`), antes `TODO` listado em "Comportamentos desconhecidos" 🔴 de `_reversa_sdd/frameless/requirements.md`.
- Agregados: preso à face do pai mais próxima, limite na borda, afundar até a espessura, Perfurar por booleana com caixa cortadora (`IS_CUTTING_OBJ`) e furo real por `CPM_CUTOUT` "Agregado: *" (D-12 a D-14). 🟡
- Folha convertida: pivô "<folha> - Eixo", varredura com parada no primeiro contato (passo 2° / 1 cm, bissecção até 0,25° / 1 mm), cache de alvos invalidado por `depsgraph_update_post` (D-17 a D-19). 🟡
- Mover Sobre: rotação pelo centro da base de A; relativa/absoluta só muda a exibição; posições salvas em `Scene.btm_saved_positions`; Substituir só com a biblioteca de módulos do usuário (D-21 a D-23; D-23 era 🔴). 
- Aviso "Projeto salvo" e registro de falha ao salvar no console (D-27). 🟡
