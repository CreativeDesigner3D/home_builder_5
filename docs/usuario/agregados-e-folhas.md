# Agregados e folhas de porta

Guia rápido para usar modelos 3D de fora no projeto, por exemplo uma porta baixada do SketchUp.
Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**, painel **Propriedades** › **Agregados e folhas**.

## 1. Trazer o modelo

Clique em **Importar modelo 3D** e escolha um arquivo **OBJ**, **FBX**, **glTF** ou **GLB**.
O Blender não abre `.skp`. Exporte do SketchUp num desses formatos, ou importe com outro addon: qualquer malha da cena pode ser convertida.

## 2. Converter em agregado

1. Selecione a malha e, **por último**, o elemento pai (um módulo, uma peça, uma parede ou um painel).
2. Clique em **Converter em agregado**. Ele fica preso à face do pai mais próxima.

Com o agregado selecionado:
- Ao mover, girar ou apagar o pai, o agregado vai junto. Ao apagar o pai, o CAFFMob Draw pergunta se os agregados vão junto.
- **Horizontal** e **Vertical** posicionam o agregado na face. Ele não sai do contorno do pai: um valor acima do limite volta ao máximo, que aparece ao lado do campo.
- **Mover agregado** arrasta com o mouse no plano da face e para na borda. Clique para confirmar; botão direito ou **Esc** volta.
- **Afastamento** positivo afasta do pai. Negativo afunda no pai, no máximo até a espessura dele.
- **Perfurar** recorta o pai onde o agregado afunda, só no 3D. Desligar devolve o pai inteiro.
- **Furo real no plano de corte** leva o recorte para a usinagem da peça pai, no plano de corte e no JSON de produção (`machining`). Ele só funciona quando o pai é uma peça de chapa e o agregado entra pela face da chapa. Sem essa marca, a produção não muda.
- **Peça de produção** põe o agregado na lista de peças, como uma placa com as medidas dele.
- **Desconverter** tira recortes e folha e devolve o objeto como estava.

## 3. Folha de porta

1. Selecione a malha da porta e, por último, o pai (o vão, o módulo ou a parede).
2. Clique em **Converter em folha de porta** e escolha o movimento:
   - **Giro:** o eixo (esquerda, direita, topo ou base), o sentido (para fora ou para dentro) e o **ângulo máximo** (até 180°).
   - **Correr:** o sentido e o **curso**.
3. Arraste a barra **Abertura** (0 a 100%). A folha se move na hora, e a viewport mostra o eixo, o caminho da borda e a posição da folha.

Se a folha encostar numa parede ou em outro objeto ao abrir, ela para no ponto do contato e fica vermelha, com o aviso
**Folha bateu em <objeto>**. A barra trava ali. Fechar é sempre livre e volta à posição original exata.

As folhas convertidas também respondem a **Abrir/Fechar Frentes** e à verificação de interferência. Como as outras
frentes, o projeto é salvo com elas fechadas.
