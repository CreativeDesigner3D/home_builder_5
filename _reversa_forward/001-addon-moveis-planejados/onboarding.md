# Onboarding: testar o incremento 1 pela primeira vez

> Feature `001-addon-moveis-planejados` · Para quem vai validar o incremento 1 no Blender.

## Pré-requisitos

- Blender 5.2 instalado (`blender --version` mostra 5.2.x).
- Repositório clonado; arquivo `promob_pacote_completo.zip` na raiz (para o teste de importação).

## 1. Instalar a extensão

```bash
python3 build.py                     # gera blendertomob.zip
```

No Blender: Edit → Preferences → Get Extensions → Install from Disk → `blendertomob.zip`. Reinicie o Blender.

## 2. Verificações automáticas

```bash
ruff check blendertomob/
python3 docs/rag/tools/check_api.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py
```

Todas devem terminar sem erro.

## 3. Unidade e vírgula decimal

1. Novo arquivo → painel lateral **Blender to Mob**.
2. Em Configurações, troque a unidade para **cm**.
3. Insira um balcão; confira que a pré-visualização e as cotas mostram cm.
4. Digite `75,5` na largura → deve aplicar 755 mm.

## 4. Configurador de Dimensões

1. Abra **Configurador de Dimensões**. A definição ativa de um projeto novo é **Padrão Brasil** (somente-leitura).
2. Clique **Duplicar** e renomeie para "Teste".
3. Na árvore: **Cozinhas → Chapas → Lateral**. Confira a imagem de referência com os lados 1–4.
4. Altere a espessura para **18 mm** e a Fita Borda 4 para **1 mm**. A lista de pendências mostra as duas alterações.
5. Clique **Cancelar** → nada muda. Repita e clique **Aplicar**.
6. Insira um balcão: a lateral deve ter 18 mm. Os balcões já existentes também passam a 18 mm.
7. Ctrl+Z desfaz a aplicação inteira de uma vez.
8. Tente digitar uma espessura fora da faixa → aparece "Valor Inválido" com a faixa permitida.

## 5. Importar o padrão do Promob

1. Extraia `configuracoes/PROMOBCONFIGURAÇÃOMEDIDASMEMOVEIS.xml` do zip.
2. Configurador → **Importar → Promob (DIMENSIONEXPORT)**.
3. Deve surgir a definição **"ME MOVEIS - COZ. ESCR."** e um relatório "mapeados × não reconhecidos".
4. Em **Cozinhas → Chapas → Lateral**: material MDF, largura máx. 2730, comprimento máx. 1810, espessura 15.
5. **Exportar → Promob** e compare com o original: os mesmos 692 pares ID/VALUE.

## 6. Lista de peças e plano de corte

1. Monte uma cozinha com 3 balcões e 2 aéreos (frameless) e um roupeiro (closets).
2. Painel **Plano de Corte** → **Gerar lista de peças**. Confira: todas as peças reais, com ID, medidas, espessura,
   material, fitas por lado e veio.
3. Aumente um aéreo até a lateral passar de 1810 mm → a peça aparece em **Incompatíveis com a chapa**.
4. **Calcular plano de corte** → chapas por material/espessura, aproveitamento e sobras.
5. Mude a largura de um balcão → o plano aparece como **desatualizado**; **Atualizar** refaz.

## 7. JSON global v2

1. **Exportar JSON global** → salve `projeto.json`.
2. Abra o arquivo: `schema_version` = `2.0.0`, `unit` = `mm`, peças com `uid` estáveis.
3. **Importar JSON global** no mesmo projeto → mesmas peças e mesmo plano.
4. Exporte de novo sem mudar nada → conteúdo igual (exceto `exported_at`).

## O que reportar

Para cada passo que falhar: número do passo, o que esperava, o que aconteceu e o `.blend` usado.


---

# Onboarding: testar o incremento 3, bloco 1 (inspeção e movimento)

## Pré-requisitos

- Extensão instalada a partir de `python3 build.py` (Blender 5.2), como no incremento 1.
- Um projeto com: um balcão frameless de porta dupla, um aéreo com basculante, um gaveteiro frameless, um gabinete
  face frame com porta e gaveta, um roupeiro closets com porta e gaveta, e uma sanca ou parede encostada na frente
  de uma das portas.

## 1. Verificações automáticas

```bash
ruff check blendertomob/
python3 docs/rag/tools/check_api.py
python3 -m unittest discover -s tests -p 'test_*.py'
blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py
```

## 2. Modo de inspeção

1. No HUD do viewport (ou no painel **Inspeção**), ligue **Abrir portas**.
2. Clique numa porta de cada linha: ela abre até 90° com animação; clique de novo: fecha.
3. Clique numa gaveta e num pullout: deslizam até o fim do curso.
4. Clique no basculante: gira em torno da aresta de cima.
5. Esc sai do modo e mantém as frentes como estão.

## 3. Gizmo com paradas

1. Selecione uma porta: aparece o controle giratório na dobradiça.
2. Arraste: a porta acompanha; perto de 45° e 90° o valor encaixa. Segure Ctrl para movimento livre.
3. Numa gaveta, o controle é uma seta no sentido de abrir.

## 4. Abrir e fechar tudo

- **Abrir tudo (90°)**, **Abrir tudo (45°)** e **Fechar tudo** no painel atuam em todas as frentes do projeto;
  com módulos selecionados, só nos selecionados.

## 5. Salvar fechado

1. Abra algumas portas e salve (Ctrl+S): a vista continua aberta.
2. Feche e reabra o arquivo: tudo aparece fechado.
3. Ligue **Salvar com frentes abertas** e repita: reabre aberto.
4. Confira no painel do plano de corte que abrir portas **não** mostrou "O projeto mudou".

## 6. Interferência

1. Clique em **Verificar interferência**.
2. A porta que bate na sanca/parede aparece na lista com o objeto atingido; o ponto fica destacado em vermelho e
   "Ir para" centraliza a vista.
3. Nenhum aviso deve citar o próprio gabinete ou a porta vizinha do mesmo vão.

## 7. Evitar Sobreposição

1. Em **CONFIGURAÇÕES**, desligue **Evitar Sobreposição** e posicione um módulo sobre outro: é permitido.
2. Ligue de novo: o posicionamento volta a respeitar os vizinhos.

## O que reportar

Frente que gira no eixo errado ou "salta" ao abrir, porta que não volta exatamente à posição fechada, interferência
falsa ou não detectada, demora perceptível no salvamento.
