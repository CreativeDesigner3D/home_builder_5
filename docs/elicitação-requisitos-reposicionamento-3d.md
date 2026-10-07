# Elicitação de Requisitos — Reposicionamento de objetos 3D em ambientes

**Fonte primária:** gravação de tela `Gravação de Tela 2026-10-06 161942.mp4`
**Duração observada:** 08min04s
**Resolução / taxa:** 1920×1032, 30 fps
**Aplicação observada:** ÉLÉDE AMBIENTES — Promob Plus Enterprise 5.60.46.6
**Idioma da interface:** português do Brasil
**Status:** especificação derivada de evidência audiovisual, pronta para validação de negócio e implementação

## 1. Convenção de evidência e confiança

Cada afirmação usa uma classificação:

- 🟢 **CONFIRMADO** — diretamente visível na gravação ou legível em texto exibido.

- 🟡 **INFERIDO** — deduzido com alta probabilidade a partir do comportamento observado; deve ser validado.

- 🔴 **LACUNA** — não determinável pela gravação; exige decisão do responsável pelo produto.

A especificação separa **comportamento observado** de **requisito recomendado**. Um requisito recomendado pode ser implementado como contrato-alvo, mas não deve ser tratado como comportamento legado confirmado sem validação.

## 2. Resumo executivo

O sistema é um editor de ambientes 3D para projetos de interiores. O fluxo analisado manipula uma cena de quarto mobiliado e demonstra como selecionar um objeto, usar outro objeto como referência, abrir a ferramenta **Reposicionar**, interpretar duas vistas auxiliares — **Vista frontal** e **Planta baixa** —, alterar deslocamento e rotação, confirmar a operação, agrupar/selecionar componentes, visualizar propriedades e dimensões, aplicar cotas e salvar o projeto.

O núcleo funcional a ser reconstruído é:

> Permitir que o usuário posicione, oriente e valide um objeto ou grupo de objetos em uma cena 3D usando interação direta e controles numéricos/visuais, preservando a relação espacial com um objeto de referência e fornecendo confirmação, desfazimento e salvamento seguro.

A gravação não demonstra autenticação, colaboração, persistência entre sessões, permissões, exportação, cálculo de colisão automatizado, unidade configurada, mensagens de erro ou comportamento responsivo. Esses pontos estão marcados como lacunas.

## 3. Escopo identificado

### 3.1 Dentro do escopo

1. Exibir uma cena 3D de ambiente.

1. Selecionar objetos e grupos.

1. Identificar visualmente o objeto selecionado.

1. Reposicionar um objeto em relação a outro objeto de referência.

1. Exibir uma janela/modal de reposicionamento.

1. Mostrar simultaneamente uma representação frontal e uma representação em planta baixa.

1. Alterar deslocamentos nos eixos X, Y e Z.

1. Alterar rotação, incluindo rotação em graus.

1. Alternar entre posição relativa e absoluta, quando aplicável.

1. Usar passo de movimentação configurável.

1. Confirmar ou substituir a posição.

1. Selecionar grupo e subcomponentes.

1. Exibir propriedades, modelos, arranjo e movimentação.

1. Exibir dimensões, limites mínimo/máximo e tamanho de grade.

1. Exibir cotas e linhas de medida na cena.

1. Navegar pela câmera 3D e trocar o enquadramento.

1. Salvar o projeto e indicar estado de salvamento.

### 3.2 Fora do escopo ou não comprovado

- Criação de conta, login e recuperação de senha.

- Catálogo completo de produtos.

- Precificação, orçamento e compra.

- Multiusuário ou colaboração em tempo real.

- Renderização final, exportação de imagens ou vídeos.

- Integração com ERP, CAD, BIM ou nuvem.

- Impressão e geração de documentação executiva.

- Cálculo normativo de acessibilidade.

- Motor de física ou detecção de colisão automática.

- Auditoria de alterações por usuário.

## 4. Linha do tempo da evidência

Os tempos são aproximados, derivados de amostragem em intervalos de 10 segundos.

| Intervalo | Evidência observada | Requisito/implicação |
| --- | --- | --- |
| 00:00–00:20 | Cena de quarto em 3D, com cama, cabeceira, criados, luminárias, armários e objetos decorativos. Um objeto aparece destacado por contorno/caixa de seleção. | A cena deve suportar múltiplos objetos, materiais, grupos e seleção visual. 🟢 |
| 00:20–00:50 | A câmera muda para enquadrar a área da cama e do criado. | Deve haver navegação de câmera sem alterar a geometria da cena. 🟢 |
| 00:50–01:20 | É aberta uma janela chamada **Reposicionar**. O texto auxiliar registra a ação de manter o botão direito sobre um objeto e arrastá-lo sobre o objeto principal de referência. | Deve existir reposicionamento relativo por gesto de arraste entre objeto móvel e referência. 🟢 |
| 01:20–02:00 | A janela mostra **Visualizar Posição Relativa**, **Passo Teclado**, **Vista frontal**, **Planta baixa**, campos X/Y/Z, rotação, **Posições Salvas**, **Substituir** e **OK**. | O modal precisa expor representação espacial, parâmetros editáveis e ações de confirmação/substituição. 🟢 |
| 02:00–02:40 | A janela é usada para mover o objeto em relação à referência; a cena mostra uma luminária/cabeceira e valores numéricos alterados. | Alterações numéricas devem atualizar a cena e vice-versa, quando o campo for editável. 🟡 |
| 02:40–03:20 | O texto auxiliar explica que o botão direito sobre um plano altera o plano de inserção. A cena passa a mostrar o ambiente de forma mais ampla, com duas luminárias. | A inserção/reposicionamento deve respeitar um plano de referência selecionável. 🟢 |
| 03:20–04:00 | Um grupo é selecionado; a barra inferior mostra dimensões, normal e rotação. A janela Reposicionar apresenta outra orientação e valores de posição. | Grupo deve ser uma unidade manipulável, preservando componentes e transformação do conjunto. 🟢 |
| 04:00–04:40 | A seleção mostra cotas no ambiente e a interface **Ferramentas — Propriedades**, com seções Arranjo, Modelos, Movimentação e Propriedades. | O sistema deve oferecer inspeção de propriedades e cotagem contextual. 🟢 |
| 04:40–05:20 | São visíveis dimensões como 1368,6, 3267,4 e 1280,7; aparece rotação de 90° no painel de movimentação. | Valores geométricos precisam ter unidade, precisão e orientação identificáveis. 🟢; unidade exata é lacuna. 🔴 |
| 05:20–06:00 | A câmera percorre o ambiente; o usuário visualiza cama, armários, janela, televisão, poltrona, tapete e decoração. | O modelo deve permitir órbita/zoom/pan e inspeção de diferentes ângulos. 🟢 |
| 06:00–06:40 | O usuário seleciona componentes e alterna a área de propriedades; linhas de cota e caixas de seleção acompanham a seleção. | Seleção e metadados devem permanecer sincronizados. 🟢 |
| 06:40–07:20 | O ambiente é exibido em vista ampla; surge mensagem **Salvando projeto — Por favor, aguarde**, com indicador de progresso. | Salvamento deve ser assíncrono, bloquear conflitos e informar progresso/estado. 🟢 |
| 07:20–07:50 | Após o salvamento, a câmera muda para uma vista superior/diagonal e continua mostrando cotas e seleção. | A visualização deve permanecer disponível durante/depois do salvamento. 🟢 |
| 07:50–08:04 | Vista final do lado da TV/poltrona; objeto selecionado e dimensões/linhas ainda visíveis. | O estado visual final deve ser preservado após navegação e salvamento. 🟢 |

## 5. Personas e objetivos

### P01 — Projetista de interiores

- Cria e ajusta ambientes.

- Precisa posicionar objetos com precisão sem perder a referência espacial.

- Alterna entre percepção visual e coordenadas numéricas.

### P02 — Modelador técnico

- Trabalha com grupos, dimensões, rotação e limites geométricos.

- Precisa verificar medidas e evitar alterações acidentais em componentes.

### P03 — Revisor/cliente interno

- Inspeciona o resultado em diferentes vistas.

- Precisa confiar que o arquivo foi salvo e que as dimensões são legíveis.

## 6. Objetivos de negócio

- **OB-01:** reduzir o tempo para alinhar e reposicionar objetos em ambientes 3D.

- **OB-02:** evitar reposicionamento impreciso baseado apenas em arraste livre.

- **OB-03:** tornar explícita a relação entre objeto móvel, objeto de referência, plano e coordenadas.

- **OB-04:** permitir conferência técnica por dimensões, limites, rotação e cotas.

- **OB-05:** preservar o projeto com salvamento confiável e feedback de operação.

## 7. Modelo conceitual do domínio

### 7.1 Entidades

- **Projeto:** unidade persistida que contém ambientes, cenas, configurações e histórico mínimo de alterações.

- **Ambiente:** espaço modelado, como quarto, com paredes, piso, teto e objetos.

- **Cena 3D:** representação renderizável de um ambiente em determinado estado de câmera.

- **Objeto:** entidade posicionável com identificador, geometria, modelo, material, dimensões e transformação.

- **Grupo:** conjunto hierárquico de objetos tratado como unidade de seleção e transformação.

- **Objeto móvel:** objeto selecionado para receber transformação.

- **Objeto de referência:** objeto usado como origem/referência do reposicionamento relativo.

- **Plano de inserção:** plano geométrico selecionável que define o contexto de inserção ou movimento.

- **Transformação:** posição X/Y/Z, rotação e, se suportado, escala.

- **Cota:** anotação dimensional vinculada a pontos, arestas, faces ou objetos.

- **Posição salva:** preset nomeado de transformação reutilizável.

- **Câmera:** posição, orientação, zoom e projeção da visualização.

- **Operação de salvamento:** processo persistente com estados iniciado, em andamento, concluído e falho.

### 7.2 Invariantes

1. Todo objeto deve ter um identificador estável dentro do projeto. 🟡

1. Uma transformação aplicada a grupo deve respeitar o sistema de coordenadas do grupo. 🟡

1. A unidade exibida deve ser consistente em campos, cotas e propriedades. 🟡

1. Cancelar o modal não pode confirmar uma transformação não aplicada. 🟡

1. O objeto de referência não deve ser movido como efeito colateral do reposicionamento do objeto móvel. 🟡

1. Seleção, cota e painel de propriedades devem referir-se ao mesmo objeto ou grupo. 🟢

1. Um salvamento em andamento não deve perder alterações já confirmadas. 🟡

## 8. Requisitos funcionais

### RF-001 — Abrir e exibir projeto

**Prioridade:** Must
O sistema deve abrir um projeto contendo pelo menos um ambiente 3D e renderizar os objetos com materiais, contornos e iluminação disponíveis.

**Critérios de aceitação**

- Dado um projeto válido, quando ele for aberto, então o ambiente selecionado deve ser exibido.

- Objetos devem ser distinguíveis visualmente.

- O sistema deve indicar o ambiente/aba atual.

### RF-002 — Selecionar objeto

**Prioridade:** Must
O sistema deve permitir selecionar um objeto por apontamento na cena e indicar a seleção por contorno, caixa, cor ou outro marcador consistente.

**Critérios**

- Clique em área pertencente a um objeto seleciona o objeto mais específico disponível.

- A seleção atual aparece no painel de propriedades e/ou barra de status.

- Selecionar outro objeto substitui a seleção, salvo quando o modo de seleção múltipla estiver ativo.

- Clicar em área vazia limpa a seleção, se não houver operação modal em andamento.

### RF-003 — Selecionar grupo e subobjeto

**Prioridade:** Must
O sistema deve suportar seleção de grupo como unidade e acesso aos componentes internos sem destruir a estrutura hierárquica.

**Critérios**

- O usuário deve distinguir grupo de objeto simples.

- Transformar o grupo deve manter os componentes relativos entre si.

- O sistema deve informar o tipo e as dimensões da entidade selecionada.

### RF-004 — Iniciar reposicionamento por gesto relativo

**Prioridade:** Must
O sistema deve permitir que o usuário mantenha o botão direito sobre um objeto móvel e o arraste sobre um objeto principal de referência para iniciar o reposicionamento relativo.

**Critérios**

- O gesto deve reconhecer origem e destino.

- Ao reconhecer o gesto, o sistema deve abrir a janela **Reposicionar** ou o equivalente definido pelo produto.

- O objeto de referência deve ficar identificado no estado da operação.

- O gesto não deve alterar o objeto se o usuário cancelar a operação.

### RF-005 — Abrir janela Reposicionar

**Prioridade:** Must
A janela deve apresentar, no mínimo, o objeto móvel, a referência, o modo relativo, vistas frontal e em planta, campos de transformação, posições salvas e ações de confirmação/cancelamento.

**Critérios**

- O modal deve informar quando não há objeto móvel ou referência válida.

- A abertura deve carregar os valores atuais da transformação.

- A janela deve permanecer associada à operação até confirmar, substituir ou cancelar.

### RF-006 — Visualizar posição relativa

**Prioridade:** Must
O sistema deve oferecer o modo **Visualizar Posição Relativa**, no qual a posição do objeto móvel seja interpretada em relação ao objeto ou plano de referência.

**Critérios**

- O modo relativo deve ser distinguível do modo absoluto.

- A alteração da referência deve recalcular a posição relativa sem alterar indevidamente a geometria do objeto.

- O sistema deve informar a origem do sistema de coordenadas utilizado.

### RF-007 — Exibir vista frontal

**Prioridade:** Must
A janela deve mostrar uma representação frontal simplificada do objeto e/ou relação espacial, com eixos identificados.

**Critérios**

- A vista deve atualizar após alterações de posição e rotação.

- O usuário deve conseguir interpretar o deslocamento vertical e horizontal.

- A vista deve indicar orientação dos eixos ou fornecer legenda equivalente.

### RF-008 — Exibir planta baixa

**Prioridade:** Must
A janela deve mostrar uma representação em planta baixa, permitindo interpretar posição no plano horizontal e orientação.

**Critérios**

- A planta deve atualizar em tempo compatível com a edição.

- O ponto de origem e os eixos devem ser identificáveis.

- Objetos de referência devem ser diferenciados do objeto móvel.

### RF-009 — Editar deslocamentos X, Y e Z

**Prioridade:** Must
O usuário deve poder informar deslocamentos nos eixos X, Y e Z por campos numéricos e/ou controles incrementais.

**Critérios**

- Campos devem aceitar números positivos, negativos e zero, conforme domínio permitido.

- Valor inválido não pode ser aplicado silenciosamente.

- A cena e as vistas devem refletir o novo valor após confirmação do campo.

- O sistema deve preservar precisão interna superior ou igual à precisão exibida.

### RF-010 — Editar rotação

**Prioridade:** Must
O sistema deve permitir informar rotação em graus, por eixo ou conforme o modelo de rotação do produto.

**Critérios**

- Deve existir indicação clara do eixo afetado.

- Valores equivalentes, como 0° e 360°, devem ser normalizados ou aceitos consistentemente.

- Rotação deve atualizar a orientação nas vistas e na cena.

- O sistema deve indicar se a rotação é relativa ao centro do objeto, ao pivô ou a outro ponto.

### RF-011 — Usar passo de movimentação

**Prioridade:** Should
O sistema deve disponibilizar o campo **Passo Teclado** ou equivalente para definir o incremento aplicado por teclas/controles.

**Critérios**

- O passo atual deve ser visível.

- Alterar o passo deve afetar somente movimentações incrementais subsequentes.

- O sistema deve validar passo positivo e dentro de limites configuráveis.

### RF-012 — Alternar posição relativa/absoluta

**Prioridade:** Should
O sistema deve permitir alternar entre transformação relativa à referência e transformação no sistema global do ambiente.

**Critérios**

- A troca de modo deve recalcular a representação sem mudar o resultado espacial até que o usuário edite um valor.

- O modo atual deve estar claramente marcado.

- O sistema deve informar a unidade e a origem de cada campo.

### RF-013 — Substituir posição

**Prioridade:** Must
A ação **Substituir** deve aplicar a posição editada à entidade selecionada, preservando o restante do projeto.

**Critérios**

- A substituição deve exigir uma entidade válida.

- O resultado deve ser visível na cena imediatamente após aplicação.

- A operação deve ser desfeita por comando de desfazer, se esse mecanismo existir.

- O objeto de referência não deve ser alterado.

### RF-014 — Confirmar e cancelar

**Prioridade:** Must
A janela deve possuir ações inequívocas para confirmar e cancelar.

**Critérios**

- **OK** confirma a transformação corrente.

- Cancelar/fechar sem confirmação descarta alterações pendentes.

- Se houver alterações não confirmadas, fechar deve solicitar decisão ou preservar rascunho explicitamente.

- O foco de teclado deve seguir a ação segura por padrão.

### RF-015 — Salvar posições reutilizáveis

**Prioridade:** Could
O sistema pode permitir criar, selecionar, substituir e remover presets de posição na área **Posições Salvas**.

**Critérios**

- Cada posição salva deve possuir nome ou identificador.

- A aplicação de um preset deve permitir pré-visualização antes da confirmação.

- Presets devem registrar referência, transformação e unidade.

### RF-016 — Alterar plano de inserção

**Prioridade:** Must
O sistema deve permitir selecionar um plano na cena, por ação contextual equivalente ao clique direito, para definir o plano de inserção.

**Critérios**

- O plano ativo deve ser visualmente indicado.

- O sistema deve impedir seleção de superfície não compatível ou informar a incompatibilidade.

- Novas inserções/reposicionamentos devem respeitar o plano ativo.

### RF-017 — Exibir painel de ferramentas e propriedades

**Prioridade:** Must
O sistema deve oferecer painéis/seções equivalentes a **Arranjo**, **Modelos**, **Movimentação** e **Propriedades**.

**Critérios**

- O painel deve indicar a entidade selecionada.

- A seção de movimentação deve mostrar deslocamento e rotação editáveis, quando suportados.

- A seção de propriedades deve mostrar dimensões e limites geométricos.

- O painel deve atualizar ao trocar a seleção.

### RF-018 — Exibir dimensões e limites

**Prioridade:** Must
O sistema deve mostrar dimensões, limite mínimo, limite máximo e tamanho de grade, quando disponíveis para a entidade.

**Critérios**

- Valores devem usar unidade e precisão configuradas.

- Limites devem ser distinguíveis de dimensões atuais.

- Campos ausentes devem ser apresentados como indisponíveis, não como zero.

### RF-019 — Criar e atualizar cotas

**Prioridade:** Must
O sistema deve exibir cotas e linhas de medida vinculadas à cena e à seleção.

**Critérios**

- Cotas devem acompanhar o objeto quando configuradas como associativas.

- A seleção deve destacar as cotas relacionadas.

- O sistema deve evitar sobreposição ilegível ou fornecer mecanismo de reposicionamento da anotação.

- A unidade deve ser consistente com a do painel de propriedades.

### RF-020 — Navegar pela cena

**Prioridade:** Must
O sistema deve permitir orbitar, aproximar, afastar e deslocar a câmera sem alterar objetos.

**Critérios**

- Navegação deve manter o estado geométrico intacto.

- O usuário deve conseguir inspecionar pelo menos vista superior/diagonal e vistas laterais.

- O sistema deve indicar quando uma ação altera câmera e não objeto.

### RF-021 — Salvar projeto com feedback

**Prioridade:** Must
O sistema deve salvar alterações do projeto e indicar claramente o estado **Salvando projeto — Por favor, aguarde** ou equivalente.

**Critérios**

- Enquanto salva, o sistema deve informar progresso ou atividade.

- O usuário não deve receber confirmação de sucesso antes da conclusão real.

- Falha deve exibir mensagem acionável e manter alterações recuperáveis.

- Salvamento concorrente deve ser serializado ou protegido contra sobrescrita.

- Após sucesso, o estado deve ser marcado como salvo.

### RF-022 — Desfazer e refazer

**Prioridade:** Should
O sistema deve permitir desfazer e refazer transformações, alterações de grupo, cotas e mudança de plano.

**Critérios**

- Cada operação confirmada deve formar uma unidade lógica de histórico.

- Cancelamentos não devem entrar no histórico.

- Salvamento não deve limpar o histórico sem informar o usuário.

## 9. Regras de negócio e interação

- **RN-01:** O reposicionamento exige uma entidade móvel e uma referência válida. 🟡

- **RN-02:** Uma referência não deve ser deslocada ao aplicar a transformação do móvel. 🟡

- **RN-03:** A transformação de grupo deve preservar a posição relativa dos filhos. 🟡

- **RN-04:** A alteração de plano de inserção deve afetar novas inserções e operações que explicitamente usam o plano. 🟡

- **RN-05:** Cotas vinculadas devem recalcular após transformação. 🟡

- **RN-06:** Campos numéricos devem rejeitar valores incompatíveis com a unidade ou domínio. 🟡

- **RN-07:** O sistema deve manter coerência entre cena, vistas auxiliares e propriedades. 🟢

- **RN-08:** Fechar o modal sem confirmar não deve aplicar alteração pendente. 🟡

- **RN-09:** A câmera pode mudar sem alterar o modelo. 🟢

- **RN-10:** O salvamento deve ocorrer após alterações confirmadas, por ação explícita ou mecanismo automático definido. 🔴 — o vídeo mostra o salvamento, mas não determina seu gatilho.

## 10. Casos de uso principais

### UC-01 — Reposicionar objeto em relação a referência

**Pré-condições:** projeto aberto; objeto móvel e referência visíveis; usuário em modo de edição.
**Fluxo principal:**

1. Usuário aponta para o objeto móvel.

1. Mantém botão direito pressionado.

1. Arrasta sobre o objeto de referência.

1. Sistema identifica origem e destino.

1. Sistema abre Reposicionar.

1. Sistema carrega vista frontal, planta, posição relativa e rotação atuais.

1. Usuário edita X/Y/Z, rotação ou usa incremento.

1. Sistema atualiza representação e pré-visualização.

1. Usuário seleciona OK/Substituir.

1. Sistema aplica transformação, atualiza cotas/propriedades e marca o projeto como alterado.

1. Usuário salva o projeto.

**Alternativas:**

- A1: destino não é objeto válido; informar erro e não abrir operação confirmável.

- A2: usuário cancela; restaurar transformação anterior.

- A3: valor inválido; manter valor anterior e apontar campo.

- A4: colisão ou limite; impedir aplicação ou advertir conforme política definida.

- A5: falha de salvamento; manter alterações em estado recuperável e informar falha.

### UC-02 — Alterar plano de inserção

1. Usuário aponta para plano/superfície.

1. Aciona o comando contextual.

1. Sistema valida compatibilidade.

1. Sistema destaca plano ativo.

1. Próxima operação compatível usa esse plano.

### UC-03 — Inspecionar grupo e dimensões

1. Usuário seleciona grupo.

1. Sistema destaca grupo e mantém filhos agrupados.

1. Painel mostra tipo, dimensões, limites e rotação.

1. Sistema mostra cotas associadas.

1. Usuário navega pela câmera para validar o resultado.

### UC-04 — Salvar projeto

1. Usuário solicita salvamento.

1. Sistema bloqueia operações conflitantes ou as enfileira.

1. Exibe estado de salvamento.

1. Persiste projeto.

1. Exibe sucesso e atualiza indicador de alteração.

## 11. Máquina de estados sugerida

```
Nenhum projeto
  -> Projeto aberto
Projeto aberto
  -> Objeto selecionado
Objeto selecionado
  -> Reposicionamento em preparação
Reposicionamento em preparação
  -> Modal Reposicionar aberto
Modal Reposicionar aberto
  -> Pré-visualizando transformação
Pré-visualizando transformação
  -> Confirmado
Pré-visualizando transformação
  -> Cancelado
Confirmado
  -> Projeto alterado
Projeto alterado
  -> Salvando
Salvando
  -> Salvo
Salvando
  -> Falha de salvamento / recuperação
```

Estados proibidos:

- Aplicar transformação sem objeto válido.

- Confirmar valores com erro não resolvido.

- Alterar referência enquanto há transformação pendente sem recalcular explicitamente.

- Declarar salvamento concluído antes da persistência.

## 12. Requisitos não funcionais

### RNF-01 — Desempenho

- Atualização de campos e pré-visualizações deve ocorrer sem atraso perceptível em cenas dentro do limite suportado.

- A interação de câmera não deve bloquear a edição.

- O salvamento deve informar progresso em operações longas.

- Meta recomendada: resposta de interação em até 100 ms para cenas padrão; pré-visualização em até 250 ms. 🟡

### RNF-02 — Precisão geométrica

- Transformações devem ser calculadas com precisão suficiente para evitar deriva acumulada.

- A precisão armazenada deve ser maior ou igual à exibida.

- A unidade deve ser configurável e persistida por projeto. 🔴

### RNF-03 — Consistência transacional

- Confirmar uma transformação deve atualizar modelo, vistas, propriedades, cotas e histórico de forma atômica.

- Falha parcial deve ser revertida ou marcada de forma explícita.

### RNF-04 — Usabilidade

- Botão direito, clique esquerdo, arraste, teclado e modal devem ter estados visuais claros.

- Campos devem apresentar rótulo, unidade, estado de erro e valor atual.

- O sistema deve evitar que a cor seja o único indicador de seleção.

### RNF-05 — Acessibilidade

- Todos os controles do modal devem ser acessíveis por teclado.

- Foco deve ser visível.

- Rótulos e mensagens devem ser legíveis por leitor de tela quando a plataforma permitir.

- Não depender apenas de cor para diferenciar referência, móvel e seleção.

### RNF-06 — Recuperação

- O sistema deve recuperar autosave ou rascunho após encerramento inesperado, se esse recurso fizer parte do produto.

- Falha de salvamento não pode descartar silenciosamente alterações confirmadas.

### RNF-07 — Observabilidade

- Registrar início/fim/falha de reposicionamento e salvamento.

- Registrar identificadores de projeto, ambiente e entidade, sem expor dados sensíveis.

- Permitir diagnóstico de inconsistências entre transformação e cotas.

### RNF-08 — Compatibilidade

- O produto deve declarar versões de sistema operacional, GPU, navegador/runtime e formatos de projeto suportados. 🔴

## 13. Contrato de dados sugerido

```json
{
  "projectId": "string",
  "environmentId": "string",
  "selection": {
    "entityId": "string",
    "entityType": "object|group",
    "referenceId": "string|null"
  },
  "transform": {
    "mode": "relative|absolute",
    "x": "number",
    "y": "number",
    "z": "number",
    "rotation": {
      "x": "number",
      "y": "number",
      "z": "number"
    },
    "unit": "string",
    "pivot": "center|origin|custom"
  },
  "insertionPlane": {
    "planeId": "string|null",
    "normal": ["number", "number", "number"]
  },
  "constraints": {
    "min": ["number", "number", "number"],
    "max": ["number", "number", "number"],
    "gridStep": "number"
  },
  "camera": {
    "position": ["number", "number", "number"],
    "target": ["number", "number", "number"],
    "projection": "perspective|orthographic"
  }
}
```

Campos `unit`, `pivot`, limites, projeção, rotação por eixo e persistência da câmera são inferências de design e precisam de validação. 🟡/🔴

## 14. Matriz de rastreabilidade

| Objetivo | Requisitos | Evidência |
| --- | --- | --- |
| OB-01 reduzir tempo | RF-002, RF-004, RF-005, RF-009, RF-010 | 00:50–04:00 |
| OB-02 aumentar precisão | RF-006, RF-007, RF-008, RF-009, RF-018, RF-019 | 01:20–05:20 |
| OB-03 explicitar referência/plano | RF-004, RF-006, RF-016 | 00:50–03:20 |
| OB-04 conferir tecnicamente | RF-017, RF-018, RF-019, RF-020 | 04:00–08:04 |
| OB-05 preservar projeto | RF-021, RF-022 | 06:40–07:20 |

## 15. Critérios de aceite ponta a ponta

### CA-01 — Reposicionamento relativo confirmado

Dado um projeto com cama, cabeceira e luminária, quando o usuário arrastar a luminária com botão direito sobre a cabeceira, então o sistema deve abrir Reposicionar, identificar a luminária como móvel e a cabeceira como referência, mostrar vista frontal e planta, permitir editar posição/rotação e aplicar a alteração sem mover a cabeceira.

### CA-02 — Cancelamento seguro

Dado um modal com alteração pendente, quando o usuário cancelar ou fechar sem confirmar, então a cena, as cotas e as propriedades devem retornar ao estado anterior.

### CA-03 — Coerência de vistas

Dado um valor alterado em X, Y, Z ou rotação, quando o usuário confirmar o campo, então a cena, a vista frontal, a planta e o painel de propriedades devem mostrar o mesmo resultado espacial.

### CA-04 — Grupo preservado

Dado um grupo com múltiplos componentes, quando o usuário mover ou rotacionar o grupo, então os componentes devem manter suas distâncias e orientações relativas.

### CA-05 — Cotas atualizadas

Dado um objeto com cotas associativas, quando sua transformação for confirmada, então as cotas devem recalcular sem permanecerem presas à posição anterior.

### CA-06 — Salvamento confiável

Dado um projeto alterado, quando o usuário salvar, então o sistema deve exibir estado de salvamento, persistir as alterações e só declarar sucesso após confirmação da persistência.

### CA-07 — Falha de salvamento

Dado um erro de armazenamento ou rede, quando o salvamento falhar, então o sistema deve informar a falha, preservar o estado editado localmente quando possível e permitir tentar novamente.

### CA-08 — Navegação sem mutação

Dado um projeto salvo, quando o usuário orbitar, aproximar ou afastar a câmera, então somente a câmera deve mudar e o modelo deve permanecer idêntico.

## 16. Perguntas de validação obrigatória

1. Qual é o nome definitivo do produto e do módulo?

1. O gesto é exatamente botão direito + arraste, ou deve existir alternativa por teclado, toque e botão configurável?

1. O que é “objeto principal de referência”: qualquer objeto, somente superfície/plano ou entidade compatível?

1. O reposicionamento relativo usa origem do objeto, centro geométrico, pivô ou ponto de ancoragem?

1. Quais são os eixos e a convenção de rotação?

1. Qual é a unidade: milímetro, centímetro, metro ou outra?

1. Qual é a precisão mínima e o arredondamento exibido?

1. Há limites de movimento e rotação? O que ocorre ao excedê-los?

1. Colisões devem bloquear, advertir ou ser permitidas?

1. A posição relativa deve preservar o contato/alinhamento com a referência?

1. “Substituir” aplica imediatamente, salva um preset ou substitui uma posição existente?

1. Como as posições salvas são nomeadas e persistidas?

1. O plano de inserção é infinito, limitado à face, ao ambiente ou ao objeto?

1. Cotas são automáticas, manuais ou ambas?

1. Como lidar com objetos ocultos, bloqueados, agrupados ou vinculados?

1. O salvamento é manual, automático ou híbrido?

1. Existe autosave e qual é a política de recuperação?

1. O projeto pode ser editado por mais de um usuário?

1. Quais formatos de importação/exportação são obrigatórios?

1. O ambiente deve funcionar offline?

1. Quais atalhos, dispositivos de entrada e leitores de tela devem ser suportados?

1. Quais métricas definem sucesso: tempo de reposicionamento, precisão, taxa de erro ou redução de retrabalho?

## 17. Riscos e decisões de arquitetura

- **Risco R-01 — Ambiguidade de coordenadas:** sem contrato explícito, dois módulos podem interpretar X/Y/Z de forma diferente. Mitigação: definir sistema global, local, unidade e pivô antes da implementação.

- **Risco R-02 — Transformação de grupos:** aplicar rotação no referencial errado pode deslocar filhos. Mitigação: testes de transformação hierárquica e invariantes de grupo.

- **Risco R-03 — Cotas dessincronizadas:** cotas não associativas podem induzir erro técnico. Mitigação: vínculo por identificador geométrico e testes após cada transformação.

- **Risco R-04 — Salvamento incompleto:** operação assíncrona pode dar falsa sensação de persistência. Mitigação: estado transacional, checksum/versão e confirmação pós-escrita.

- **Risco R-05 — Gesto difícil de descobrir:** botão direito + arraste é pouco evidente. Mitigação: affordance visual, tooltip, tutorial e comando alternativo.

- **Risco R-06 — Cenas grandes:** pré-visualização pode degradar com muitos polígonos. Mitigação: representação simplificada durante transformação e atualização incremental.

## 18. Plano de testes recomendado

### Testes funcionais

- Seleção de objeto simples, grupo, filho, plano e área vazia.

- Arraste válido e inválido entre objeto móvel e referência.

- Valores positivos, negativos, zero, decimais, vazio, texto e overflow.

- Rotação 0°, 90°, 180°, 270°, 360° e valores negativos.

- Modo relativo versus absoluto.

- Aplicação, cancelamento, fechar modal e desfazer.

- Mudança de plano de inserção.

- Atualização de cotas, limites e propriedades.

- Salvamento concluído, lento, falho, interrompido e repetido.

### Testes geométricos

- Preservação de distância entre filhos de grupo.

- Transformação em cada eixo isoladamente.

- Transformação em referência rotacionada.

- Precisão acumulada após 100 operações.

- Objeto encostado, sobreposto, fora do ambiente e dentro de limite.

### Testes de usabilidade

- Usuário novo descobre o gesto sem treinamento.

- Usuário identifica claramente móvel e referência.

- Usuário entende a diferença entre vista frontal e planta.

- Usuário consegue operar apenas pelo teclado.

### Testes de desempenho

- Cenas pequenas, médias e grandes.

- Atualização de cena durante arraste.

- Câmera durante renderização.

- Salvamento com arquivos grandes.

## 19. Definição de pronto para implementação

A feature só deve ser considerada pronta quando:

- todas as perguntas críticas 1–10 e 16–20 estiverem respondidas;

- sistema de coordenadas, unidade, pivô e política de colisão estiverem documentados;

- RF-001 a RF-022 tiverem testes automatizados ou manuais reproduzíveis;

- houver teste ponta a ponta equivalente ao CA-01;

- cancelamento, desfazer e falha de salvamento estiverem cobertos;

- as cotas forem verificadas após transformação simples e de grupo;

- a documentação de atalhos e estados do modal existir;

- nenhum requisito marcado 🔴 permaneça implicitamente decidido;

- o comportamento implementado seja comparado com a gravação e as divergências sejam registradas.

## 20. Conclusão

A gravação não é apenas uma demonstração visual de arraste: ela revela um modelo operacional composto por **seleção hierárquica**, **referência espacial**, **transformação relativa**, **vistas ortogonais auxiliares**, **propriedades geométricas**, **cotas**, **navegação de câmera** e **persistência com feedback**. A implementação deve tratar essas partes como uma única operação transacional; caso sejam construídas como controles independentes, haverá risco de divergência entre o que o usuário vê, o que as cotas informam e o que é salvo.

O documento é suficiente para iniciar descoberta técnica, desenho de contratos e prototipação sem consultar imagens. As decisões marcadas como 🔴 devem ser resolvidas com o responsável pelo produto antes de congelar a especificação.