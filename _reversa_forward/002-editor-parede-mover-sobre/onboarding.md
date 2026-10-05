# Onboarding: testar a feature 002 pela primeira vez

## Pré-requisitos

- Blender 5.2 com a extensão instalada a partir de `python3 build.py`.
- Um projeto com:
  - uma sala de 4 paredes desenhadas pelo construtor (aba CONSTRUTOR › "Desenhar Paredes");
  - um balcão frameless e um aéreo face frame numa parede;
  - um starter de closets em outra parede;
  - uma janela.

## 1. Verificações automáticas

```bash
ruff check blendertomob/
python3 docs/rag/tools/check_api.py
python3 -m unittest discover -s tests -p 'test_*.py'
blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py
```

## 2. Janela de propriedades (bloco 1)

1. Abra a barra lateral (N), aba **Blender to Mob**.
2. Selecione, um de cada vez: a parede, o balcão, o aéreo, o starter de closets, uma gaveta e a janela. Confira:
   - a parede mostra o grupo **Parede** e o botão **Abrir editor de paredes**;
   - os gabinetes, de qualquer biblioteca, mostram **Dimensões**, **Cotas** e **Ações**;
   - a gaveta mostra **Abrir** e o módulo dela;
   - no 3D, as cotas do módulo selecionado aparecem até as paredes, o piso e o teto.
3. No balcão, digite 75 mm na **cota anterior**: ele fica a 75 mm do vizinho. Desfaça com Ctrl+Z (um passo).

## 3. Mover Sobre (bloco 2)

1. Ligue **Mover Sobre** (painel ou HUD).
2. Pressione o botão direito sobre o aéreo, arraste até o balcão e solte. A janela abre com as vistas **superior** e **frontal**, só com os dois objetos.
3. Na vista superior, clique perto da linha de **profundidade 0** do balcão: a frente do aéreo alinha com a do balcão.
4. Na vista frontal, clique acima do topo do balcão: o aéreo fica empilhado sobre ele.
5. **Cancelar** devolve o aéreo à posição original; **Confirmar** grava a posição em um passo de desfazer.
6. Desligue o modo: o botão direito volta a abrir o menu de contexto.

## 4. Editor de Paredes (bloco 3)

1. Botão direito na parede › **Editar Paredes…**: abre a janela com a planta da sala.
2. Clique na linha **externa** de uma parede: o painel mostra a medida externa. Na **interna**, a interna (diferença = espessuras dos cantos).
3. Mude o **comprimento** de um trecho e arraste um vértice: o painel acompanha.
4. **Cancelar**: o 3D fica igual. Repita e dê **OK**: as paredes, os encontros, o piso e o teto são refeitos.
5. Num ambiente vazio, use **Construir Parede**: clique, digite 3900 Enter, 2700 Enter, 3900 Enter, clique no ponto inicial e responda **Sim**.

## 5. Geometria e operações de parede (bloco 4)

1. Crie uma **placa** pelos cantos de uma parede, com espessura de 18 mm; marque **peça de fabricação** e gere a lista de peças: a placa aparece.
2. Remova uma parede com **Segmento** e **Remover módulos que estão na parede**.
3. **Rebaixe** a parede da frente: o interior fica visível e o pé-direito continua o mesmo nas propriedades.

## 6. Revisão de 2026-10-05 (portas, módulos no OK, paredes de outra camada)

1. Coloque uma porta de ambiente, selecione-a e clique **Abrir** na janela de propriedades: aparece a folha 3D e ela gira para o lado do símbolo 2D. Salve e reabra: a porta está fechada.
2. Repita com "Inside/Outside" e "Left/Right" (setas ↑/↓ na colocação) e com a porta dupla.
3. No Editor de Paredes, apague (Delete) o trecho de uma parede com balcão e clique **OK**: aparece a lista e a caixa **Remover os módulos junto?**. Sem marcar, o segundo OK deixa o balcão solto no lugar; marcando, o balcão sai.
4. Desenhe paredes com **Construir Parede** do painel antigo (camada nova), selecione-as e abra o Editor de Paredes: responda **Converter** (ficam editáveis; no OK viram paredes do Home Builder 5) ou **Só referência** (ficam tracejadas).

## 7. Revisão pós-auditoria ao vivo

0. Antes: em **Preferências › Add-ons**, remova a entrada antiga "blendertomob" (fora das extensões), que dá erro ao abrir o Blender.
1. No Editor de Paredes, desenhe uma sala no sentido **anti-horário** e outra no **horário** (3000 × 2000): nas duas, a linha interna (tracejada) mede 3.000 e 2.000, a espessura fica do lado de fora e, após o OK, um balcão encostado e uma porta "para dentro" ficam/abrem para dentro.
2. Selecione um trecho e troque a **Direção** (Direita/Esquerda): a espessura troca de lado e a medida interna não muda.
3. Clique na linha interna de um trecho, digite `3500` e Enter: a interna vira 3.500 e a externa 3.500 + espessuras. Clique num vértice e digite: muda o trecho que termina nele.
4. Mude algo e clique **Cancelar** (agora no fim do painel): aparece a confirmação. Esc também pergunta.
5. Ligue **Mover Sobre** e arraste com o botão direito em Modo Objeto: abre a janela de alinhamento.
6. Selecione uma porta de ambiente: o console não mostra erro.
7. Desligue e religue a extensão: nenhum aviso "registered before".

## 8. Fechamento da sala e pé-direito

1. Em Configurações (aba Home Builder), defina o pé-direito do projeto (ex.: 2.700). Abra o Editor de Paredes: em **Novas paredes**, o Pé-direito já vem 2.700.
2. Desenhe três trechos e aproxime o cursor do ponto inicial: ele gruda no ponto (anel de destaque, "Fechar"). Clique: aparece "Deseja fechar a parede?"; Sim fecha.
3. Desenhe digitando 3000, 2000, 3000 e 2000 (Enter em cada): ao voltar ao início, aparece a mesma pergunta.
4. Abra uma sala com uma parede de altura diferente: no OK aparece a lista e a caixa **Igualar ao pé-direito do projeto** (marcada).
5. Em nenhum caso o OK deixa a última parede solta no canto.
6. Mude o pé-direito nas Configurações (ex.: 2.700 → 2.800): todas as paredes de altura cheia passam a 2.800; Mureta, meia-parede e parede falsa ficam como estão. Ctrl+Z volta.
7. No "Desenhar Paredes" (3D), desenhe três paredes e aproxime do ponto inicial: o cursor gruda; clique: aparece "Deseja fechar a parede?" no cabeçalho; Enter fecha, Esc continua desenhando. Digitar a medida que volta ao início também pergunta.

## O que reportar

- Linha interna e externa trocadas.
- Paredes desalinhadas depois do OK.
- Alinhamento do "Mover Sobre" com folga ou sobreposição.
- Botão direito que não volta ao normal.
- Cota que não move o módulo como esperado.
- Folha da porta abrindo para o lado errado ou fora do vão.
- Paredes convertidas fora do lugar ou com espessura diferente.
