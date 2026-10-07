# Personalizar módulos e salvar na biblioteca

Guia rápido da personalização por módulo.
Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**, painel **Propriedades**.

## 1. O que dá para mudar

Selecione um módulo inserido (qualquer peça dele serve) e abra **Modelos — Personalizar módulo**.
A mudança vale só para esse módulo. Os outros módulos do mesmo tipo e o catálogo não mudam.

Cada vão do módulo aparece numa caixa (**Vão 1**, **Vão 2**…), com:
- **Frente:** porta à esquerda, à direita, duas portas, gavetas, basculante, painel fixo ou vazio. Em **Gavetas**, informe a quantidade.
- **Estilo:** por exemplo, vidro ou 5 peças, só nas frentes desse vão. Uma porta menor que o mínimo do estilo continua lisa, e o painel mostra o aviso.
- **Puxador:** o modelo e a posição (topo, meio ou base). **Sem puxador** retira. Marque **Aplicar a todas as frentes** para usar o mesmo em todo o módulo.
- **Material das frentes** do vão.
- **Interior:** prateleiras, divisórias e gavetas internas. Em **Alturas**, digite as alturas das prateleiras a partir da base do vão, separadas por `;` (por exemplo `200; 450`). Deixe vazio para espaçamento igual.

Abaixo dos vãos, em **Materiais**, escolha o material por grupo: **Caixa**, **Frentes**, **Fundo** e **Interno**.
Com uma peça selecionada, você também pode trocar só ela. O material da peça vence o do grupo.

O **X** de cada vão limpa o estilo, o puxador e o material daquele vão.

## 2. O que cada biblioteca permite

| | Frameless | Face frame | Closets | Módulo rápido |
|---|---|---|---|---|
| Frentes | todas | todas | portas, gavetas, vazio | portas, basculante, vazio |
| Estilo por frente | sim | sim | sim (estilos do closets) | não tem estilos |
| Puxador por frente | sim | sim | sim | sim |
| Material por grupo/peça | sim | sim | sim | caixa, interno, fundo e portas |
| Prateleiras | sim, com alturas | sim (iguais) | sim (iguais) | sim (iguais) |
| Divisórias | sim | uma por vez | não | não |
| Gavetas internas | sim | sim | use a frente Gavetas | não |

Quando a biblioteca não tem um recurso, o botão aparece apagado e o painel explica o motivo.

A personalização fica gravada no módulo. Mudar a largura, trocar o estilo geral do projeto ou recalcular o módulo
não a apaga.

## 3. Salvar como módulo

1. Com o módulo personalizado selecionado, clique em **Salvar como módulo**.
2. Digite o **Nome** e a **Categoria** (por exemplo, "Aéreos").
3. Se já existir um módulo com esse nome na categoria, a janela avisa. Marque **Substituir o módulo existente** para gravar por cima, ou mude o nome.

O módulo vai para a pasta de dados do CAFFMob Draw (`modules/<categoria>/`), com miniatura.

## 4. Usar a biblioteca de módulos

Abra **Biblioteca de módulos** no painel **Propriedades**:
- Clique no nome do módulo e depois no lugar onde ele vai ficar. **R** gira 90°; botão direito ou **Esc** cancela.
- Inserido em outro projeto, o módulo vem com frentes, puxadores, materiais e divisões iguais e continua paramétrico.
- Se o projeto não tiver um estilo usado pelo módulo, o aviso lista os estilos ausentes. O módulo mantém a aparência com que foi salvo.
- O lápis renomeia, a lixeira apaga (pede confirmação) e **Abrir pasta** mostra os arquivos.
