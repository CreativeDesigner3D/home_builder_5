#!/usr/bin/env python3
"""Busca local no RAG do Manual de Treinamento Promob (stdlib, sem embeddings).

Ranking = BM25 sobre o texto dos chunks (acentos removidos, stopwords em português)
+ bônus quando os termos aparecem no título/caminho da seção.
Gere o índice antes com: python3 docs/rag/tools/build_promob_rag.py

Exemplos:
    python3 docs/rag/tools/promob_search.py "espessura da serra plano de corte"
    python3 docs/rag/tools/promob_search.py "pé-direito parede" -k 3 --full
    python3 docs/rag/tools/promob_search.py "cotas" --chapter 13
    python3 docs/rag/tools/promob_search.py --toc | grep -i orçamento
    python3 docs/rag/tools/promob_search.py "folha carimbo" --json
"""

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAG = Path(__file__).resolve().parents[1] / "promob"
CHUNKS = RAG / "index" / "chunks.jsonl"
TOC = RAG / "index" / "toc.tsv"

STOP = set("""a o as os um uma uns umas de da do das dos em na no nas nos por pela pelo pelas pelos para com sem
e ou que se ao aos à às é ser são foi como mais menos este esta estes estas esse essa isso isto ele ela
seu sua seus suas também já não sim pode podem deve devem quando onde qual quais ser será após antes
entre sobre até cada todo toda todos todas então clique selecione opção opções""".split())
K1, B = 1.4, 0.75


def fold(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def tokenize(text):
    out = []
    for tok in re.findall(r"[a-z0-9]+", fold(text)):
        if tok in STOP or len(tok) < 2:
            continue
        out.append(tok)
        if len(tok) > 4 and tok.endswith("s"):  # plural simples
            out.append(tok[:-1])
    return out


def load():
    if not CHUNKS.exists():
        sys.exit("Índice não encontrado. Rode: python3 docs/rag/tools/build_promob_rag.py")
    rows = [json.loads(line) for line in CHUNKS.open(encoding="utf-8")]
    docs = [Counter(tokenize(r["text"])) for r in rows]
    heads = [set(tokenize(r["heading"])) for r in rows]
    df = Counter(t for d in docs for t in d)
    avg = sum(sum(d.values()) for d in docs) / max(len(docs), 1)
    return rows, docs, heads, df, avg


def search(query, k=8, chapter=None):
    rows, docs, heads, df, avg = load()
    q = tokenize(query)
    n = len(rows)
    scored = []
    for r, d, h in zip(rows, docs, heads):
        if chapter and r["chapter"] != str(chapter):
            continue
        dl = sum(d.values())
        s = 0.0
        for t in set(q):
            if t not in d:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * d[t] * (K1 + 1) / (d[t] + K1 * (1 - B + B * dl / avg))
            if t in h:
                s += 1.5 * idf
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    return scored[:k]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*", help="consulta em texto livre")
    ap.add_argument("-k", type=int, default=8, help="número de resultados (padrão 8)")
    ap.add_argument("--chapter", help="filtra pelo número do capítulo (ex.: 23)")
    ap.add_argument("--full", action="store_true", help="imprime o texto completo do chunk")
    ap.add_argument("--json", action="store_true", help="saída JSON (para agentes)")
    ap.add_argument("--toc", action="store_true", help="imprime o sumário (num, título, parte, página, caminho)")
    args = ap.parse_args()

    if args.toc:
        print(TOC.read_text(encoding="utf-8"), end="")
        return
    if not args.query:
        ap.error("informe a consulta ou use --toc")
    hits = search(" ".join(args.query), args.k, args.chapter)
    if args.json:
        print(json.dumps([dict(score=round(s, 2), **r) for s, r in hits], ensure_ascii=False, indent=2))
        return
    for i, (s, r) in enumerate(hits, 1):
        body = r["text"].split("] ", 1)[-1]
        print(f"#{i} [{s:.1f}] {r['heading']}  (p. {r['pages'][0]}–{r['pages'][1]})")
        print(f"    docs/rag/promob/{r['path']}")
        print(body if args.full else "    " + re.sub(r"\s+", " ", body)[:300])
        print()


if __name__ == "__main__":
    main()
