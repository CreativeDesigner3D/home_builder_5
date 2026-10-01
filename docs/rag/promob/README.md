# RAG — Manual de Treinamento Promob

Base consultável do **Manual Promob V-1.17.1 (2016)** (`manual-treinamento-promob.pdf`, 474 páginas), a referência de
produto que o BlenderToMob imita. Use para decisões de **comportamento e UX** (como o Promob insere, cota, imprime,
orça e corta), não para API do Blender (essa fica em [`../blender-api/`](../README.md)).

| Item | Conteúdo |
|---|---|
| `corpus/NN-<capitulo>.md` | 32 capítulos em Markdown, seções numeradas como títulos, marcadores `<!-- p. N -->` com a página do PDF |
| `index/chunks.jsonl` | ~430 chunks (1 por seção, ≤ 6000 caracteres) com `num`, `heading`, `pages`, `path` |
| `index/toc.tsv` | Sumário completo: 482 entradas (número, título, parte, página, arquivo#âncora) |
| `index/manifest.json` | Hash do PDF, contagens e títulos não localizados |

> `corpus/` e `index/` **não são versionados** (`.gitignore` local): reproduzem texto proprietário da Promob, como o
> próprio PDF. Figuras e tabelas em imagem não entram (ex.: requisitos de hardware, tabela de atalhos).

## Gerar

```bash
python3 docs/rag/tools/build_promob_rag.py            # lê manual-treinamento-promob.pdf da raiz (precisa de pdftotext)
```

## Consultar

```bash
python3 docs/rag/tools/promob_search.py "colisão entre módulos"
python3 docs/rag/tools/promob_search.py "cotagem automática" -k 3 --full
python3 docs/rag/tools/promob_search.py "espessura da serra" --chapter 23
python3 docs/rag/tools/promob_search.py --toc | grep -i viewport
python3 docs/rag/tools/promob_search.py "protótipo de impressão" --json
```

A busca é BM25 sem acentos, com stopwords em português e bônus para termos no título da seção.

## Mapa rápido

| Tema | Capítulos |
|---|---|
| Interface, biblioteca de módulos, dados do cliente | 2 |
| Paredes, planos de inserção, colisão, cotas de posição | 3, 5, 7, 9 |
| Inserir/mover módulos, modelos e estilos, puxadores, preferências (unidade, incremento) | 4 |
| Configurador de dimensões, construtor de armários, favoritos | 6, 10, 19 |
| Impressão: viewport, cotas, cotagem/documentação automática, escala, protótipos | 13 |
| Render e apresentação | 14–18 |
| Orçamento e preços | 20 |
| Promob Cut: edições, plano de corte, sobras, etiquetas | 21–23 |
| Atividades guiadas | 24–31 |

## Protocolo para agentes

Ao decidir comportamento de uma feature "estilo Promob", busque aqui primeiro e cite
`docs/rag/promob/corpus/<arquivo>.md#<âncora>` (p. N). O manual descreve a versão de 2016 e varia por "Fabricante" e
edição (Lite, Base, Plus, Arch…); trate como referência de UX, não como contrato.
