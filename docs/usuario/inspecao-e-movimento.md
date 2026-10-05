# Abrir portas e gavetas, interferência e sobreposição

Guia rápido para conferir um projeto abrindo portas, basculantes e gavetas, antes de mostrar ao cliente ou mandar para a produção.
Funciona nos móveis de cozinha (frameless), face frame, dormitório (closets) e no Módulo Rápido.
O painel fica na barra lateral da Viewport 3D (tecla **N**), aba **Blender to Mob** › **CONSTRUTOR** › **Inspeção de Portas e Gavetas**.

## 1. Abrir com um clique

1. Clique em **Abrir Portas e Gavetas**. O botão também aparece no HUD da viewport no modo de seleção **Parts**, em qualquer linha de produto, e na pílula **Open Door** dos closets.
2. Clique numa porta, basculante ou gaveta: ela abre com animação. Clique de novo e ela fecha.
   Clicar no puxador ou na caixa da gaveta também vale.
3. **Esc** ou o botão direito saem do modo; as frentes ficam como estão.

O ângulo do clique é escolhido em **Ângulo do clique** (90° ou 45°). As gavetas sempre abrem o curso inteiro.

## 2. Ajustar o ângulo à mão

Selecione uma porta (ou uma peça dela). Na dobradiça aparece um controle giratório laranja; arraste para abrir.
- Perto de **0°, 45° e 90°** o valor encaixa. Para movimento livre, desligue **Encaixar em 0°, 45° e 90°** no painel.
- Numa gaveta, o controle é uma seta no sentido de abrir.
- O limite é 90° em todas as linhas.

## 3. Abrir e fechar tudo

- **Abrir tudo 90°** e **45°** abrem todas as frentes do projeto. Com 45°, as gavetas abrem pela metade.
- **Fechar tudo** fecha todas.

Abrir portas é só conferência: não entra no Ctrl+Z, não muda nenhuma peça e não deixa o plano de corte desatualizado.

## 4. O arquivo é salvo fechado

Ao salvar (Ctrl+S), o arquivo vai com tudo fechado e a tela continua como estava.
Depois de salvar com frentes abertas, o arquivo aparece como modificado. Isso é esperado: as frentes foram reabertas na tela.
Para guardar o projeto aberto (por exemplo, para um render), ligue **Salvar com Frentes Abertas**.

## 5. Verificar interferência

1. Clique em **Verificar Interferência**.
2. O BlenderToMob gira cada porta de fechada até 90° e desliza cada gaveta até o fim. Ele avisa quando uma delas bate em outro objeto, como parede, sanca, módulo vizinho ou geometria livre.
3. A lista mostra **módulo › frente × objeto atingido**. A lupa centraliza a vista no ponto do choque, que fica marcado com uma cruz vermelha.
4. O próprio módulo não conta (a porta encosta na lateral dele normalmente). Encostar sem atravessar também não conta.

A mensagem diz quantas frentes foram verificadas. "Sem interferência" vale só para elas: se aparecer "Nenhuma frente verificada", o projeto não tem portas ou gavetas reconhecidas.

## 6. Evitar Sobreposição

Em **CONFIGURAÇÕES › Unidade & Precisão**, a opção **Evitar Sobreposição** controla o posicionamento dos módulos na parede:
- **ligada** (padrão): o módulo não ocupa o espaço de outro nem passa por paredes;
- **desligada**: o módulo pode ser colocado sobre outro. Portas e janelas da parede continuam sendo respeitadas.
