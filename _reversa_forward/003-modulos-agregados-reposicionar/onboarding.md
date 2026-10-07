# Onboarding: testar módulos personalizáveis, agregados e Mover Sobre ampliado

> Feature: `003-modulos-agregados-reposicionar` · Para quem vai testar pela primeira vez no Blender 5.2

## Preparação

1. `python3 build.py` e instale `caffmob_draw.zip` (Editar › Preferências › Extensões › Instalar do disco).
2. Arquivo novo, unidade da cena em milímetros. Desenhe um ambiente com 4 paredes (Desenhar Paredes).
3. Abra a barra lateral (N), aba **CAFFMob Draw**.

## I1/I2: personalizar e salvar módulo

Repita para um módulo de cada biblioteca (frameless, face frame, closets e o módulo rápido `btm`):

1. Insira um aéreo de 80 cm com duas portas e selecione-o.
2. Em **Propriedades › Modelos › Personalizar módulo**, confira as seções Frentes, Puxadores, Materiais e Divisões
   internas. Seção sem suporte aparece cinza com o motivo.
3. Troque as portas por 3 gavetas; depois volte a portas e aplique o estilo vidro só na porta esquerda.
4. Troque o puxador da porta direita para um perfil e a posição para Base; marque "Aplicar a todas" e confira.
5. Materiais: Frentes = laca branca, Caixa = MDF carvalho.
6. Divisões: 2 prateleiras; depois digite as alturas.
7. Mude a largura para 60 cm: tudo que você personalizou deve continuar.
8. **Salvar como módulo** → nome "Aéreo teste", categoria "Aéreos". Salve de novo com o mesmo nome: deve perguntar.
9. Arquivo novo → insira "Aéreo teste" pela biblioteca do usuário: vem igual.

Esperado: nenhum outro módulo do mesmo tipo muda; Ctrl+Z desfaz cada passo.

## I3: agregados

1. **Importar modelo** (OBJ, FBX ou glTF) de uma porta ou nicho.
2. Selecione a malha e depois a lateral de um roupeiro; **Converter em agregado**.
3. Mova o roupeiro: o agregado vai junto. Arraste o agregado para fora da lateral: ele para na borda.
4. Afastamento −10 mm numa lateral de 18 mm; tente −30 mm: o campo mostra −18 mm.
5. Ligue **Perfurar**: o furo aparece no 3D. Gere o plano de corte: a peça sai sem usinagem.
6. Marque **Furo real no plano de corte** e exporte o JSON: a lateral traz `machining` com o retângulo.
7. **Desconverter**: o furo some e a malha fica solta na mesma posição.

## I4: folha de porta

1. Importe uma porta; selecione a malha e o vão; **Converter em folha de porta**, giro à direita, máximo 180°.
2. Coloque uma parede a 30 cm da dobradiça e arraste a barra até 100%: a folha para encostada, a barra trava e
   aparece "Folha bateu em Parede". Volte a 0%: fecha na posição exata.
3. Converta outra folha como **correr**, curso 80 cm: 50% desliza 40 cm.
4. Salve o arquivo com a folha aberta e reabra: ela volta fechada (salvar fechado da 001).

## I5: Mover Sobre ampliado

1. Ligue **Mover Sobre**, arraste com o botão direito um nicho até um painel.
2. Digite X = 150 mm, Rotação = 90°; Cancelar: volta exatamente; nenhum passo de desfazer.
3. Repita e Confirmar; Ctrl+Z volta.
4. Passo 10 mm: seta direita soma 10 mm.
5. Desligue "Visualizar posição relativa": os números mudam, o objeto não.
6. **Salvar posição** "nicho centrado" e aplique a outro par nicho/painel.
7. **Substituir** por um módulo de 60: mantém o canto de referência.
8. Botão direito numa face (modo desligado) › **Usar como plano de inserção**; insira um módulo: ele apoia na face.
9. Salve o arquivo: a barra de status mostra "Projeto salvo".

## Testes automáticos

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
ruff check caffmob_draw/
python3 docs/rag/tools/check_api.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_003_smoke.py
```
