#!/usr/bin/env python3
"""Local retrieval over the Blender 5.2 API RAG corpus (stdlib only, no embeddings).

Ranking = BM25 over chunk text + boosts for exact symbol / heading matches.
Also covers the curated project knowledge in docs/rag/project/*.md.

Examples:
    python3 docs/rag/tools/rag_search.py "bmesh extrude face region"
    python3 docs/rag/tools/rag_search.py "Operator invoke modal" -k 3 --full
    python3 docs/rag/tools/rag_search.py --symbol bpy.types.NodesModifier.properties
    python3 docs/rag/tools/rag_search.py "draw handler POST_PIXEL" --category gpu
    python3 docs/rag/tools/rag_search.py "gotcha" --category guide --json
"""

import argparse
import json
import math
import pickle
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAG = Path(__file__).resolve().parents[1]
API = RAG / "blender-api"
CHUNKS = API / "index" / "chunks.jsonl"
SYMBOLS = API / "index" / "symbols.tsv"
PROJECT = RAG / "project"
CACHE = API / "index" / ".bm25.cache.pickle"

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+")
CAMEL_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")
STOP = set("the a an of to and or is in for be are this that with as it on by from if not at can will".split())
K1, B = 1.4, 0.75


def tokenize(text):
    out = []
    for tok in TOKEN_RE.findall(text):
        low = tok.lower()
        if low in STOP:
            continue
        out.append(low)
        # Split snake_case and CamelCase identifiers into parts as well.
        if "_" in low:
            out.extend(p for p in low.split("_") if p and p not in STOP)
        camel = CAMEL_RE.findall(tok)
        if len(camel) > 1:
            out.extend(p.lower() for p in camel)
    return out


def load_project_chunks():
    chunks = []
    for md in sorted(PROJECT.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text else md.stem
        for i, part in enumerate(re.split(r"\n(?=## )", text)):
            head = part.splitlines()[0].lstrip("# ").strip() if part.strip() else ""
            chunks.append({
                "id": f"project/{md.stem}#{i}", "page": f"project/{md.stem}", "title": title,
                "category": "project", "heading": head, "anchor": "", "symbols": [],
                "path": f"../project/{md.name}", "text": f"[{title}] {head}\n\n{part.strip()}",
            })
    return chunks


def build_index():
    chunks = [json.loads(line) for line in open(CHUNKS, encoding="utf-8")]
    chunks += load_project_chunks()
    tfs, df, lengths = [], Counter(), []
    for c in chunks:
        toks = tokenize(c["text"])
        tf = Counter(toks)
        tfs.append(tf)
        df.update(tf.keys())
        lengths.append(len(toks))
    postings = defaultdict(list)
    for i, tf in enumerate(tfs):
        for t, n in tf.items():
            postings[t].append((i, n))
    idx = {"chunks": chunks, "postings": dict(postings), "df": df, "lengths": lengths,
           "avgdl": sum(lengths) / max(len(lengths), 1), "mtime": index_mtime()}
    try:
        with open(CACHE, "wb") as f:
            pickle.dump(idx, f, protocol=pickle.HIGHEST_PROTOCOL)
    except OSError:
        pass
    return idx


def index_mtime():
    files = [CHUNKS] + list(PROJECT.glob("*.md"))
    return max(p.stat().st_mtime for p in files if p.exists())


def load_index(rebuild=False):
    if not rebuild and CACHE.exists():
        try:
            with open(CACHE, "rb") as f:
                idx = pickle.load(f)
            if idx.get("mtime") == index_mtime():
                return idx
        except Exception:
            pass
    return build_index()


def search(idx, query, k=8, category=None):
    chunks, N = idx["chunks"], len(idx["chunks"])
    scores = defaultdict(float)
    qtoks = tokenize(query)
    for t in set(qtoks):
        plist = idx["postings"].get(t)
        if not plist:
            continue
        idf = math.log(1 + (N - len(plist) + 0.5) / (len(plist) + 0.5))
        for i, tf in plist:
            dl = idx["lengths"][i]
            scores[i] += idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * dl / idx["avgdl"]))
    # Boosts: dotted symbols in the query, heading/title overlap, curated project docs.
    dotted = [q for q in re.findall(r"[A-Za-z_][\w.]*\.[\w.]+", query)]
    qset = set(qtoks)
    for i in list(scores):
        c = chunks[i]
        head = set(tokenize(c["heading"] + " " + c["title"]))
        scores[i] += 1.5 * len(qset & head)
        for d in dotted:
            if any(s == d or s.endswith("." + d) or s.startswith(d + ".") for s in c["symbols"]) or d in c["heading"]:
                scores[i] += 25
        if c["category"] == "project":
            scores[i] *= 1.3
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    out = []
    for i, s in ranked:
        c = chunks[i]
        if category and not (c["category"] == category or c["category"].startswith(category)):
            continue
        out.append((s, c))
        if len(out) >= k:
            break
    return out


def lookup_symbol(name):
    hits = []
    with open(SYMBOLS, encoding="utf-8") as f:
        next(f)
        for line in f:
            sym, role, path = line.rstrip("\n").split("\t")
            if sym == name or sym.endswith("." + name):
                hits.append((sym, role, path))
    return hits


def section_for(path):
    """Return the Markdown of the member/section an anchor points to."""
    file, _, anchor = path.partition("#")
    p = API / file
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    if not anchor:
        return text[:4000]
    start = text.find(f'<a id="{anchor}"></a>')
    if start < 0:
        return ""
    nxt = text.find('<a id="', start + 10)
    return text[start:nxt if nxt > 0 else None].strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="*", help="free-text query")
    ap.add_argument("-k", type=int, default=8, help="number of results (default 8)")
    ap.add_argument("--category", help="filter: bpy.types, bpy.ops, bpy.props, bmesh, gpu, mathutils, guide, project, enum_items...")
    ap.add_argument("--full", action="store_true", help="print full chunk text")
    ap.add_argument("--json", action="store_true", help="JSON output (for agents/pipelines)")
    ap.add_argument("--symbol", help="exact symbol lookup via objects.inv (e.g. bpy.types.Object.matrix_world)")
    ap.add_argument("--rebuild", action="store_true", help="rebuild the BM25 cache")
    args = ap.parse_args()

    if args.symbol:
        hits = lookup_symbol(args.symbol)
        if not hits:
            print(f"symbol not found in Blender 5.2 API: {args.symbol}", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps([{"symbol": s, "role": r, "path": f"docs/rag/blender-api/{p}",
                               "text": section_for(p)} for s, r, p in hits[:5]], ensure_ascii=False, indent=1))
            return
        for sym, role, path in hits[:5]:
            print(f"== {sym}  ({role})  -> docs/rag/blender-api/{path}\n")
            print(section_for(path) + "\n")
        return

    if not args.query:
        ap.print_help()
        return
    idx = load_index(args.rebuild)
    results = search(idx, " ".join(args.query), args.k, args.category)
    if args.json:
        print(json.dumps([{"score": round(s, 2), **{k: c[k] for k in ("id", "title", "heading", "category", "path")},
                           "text": c["text"]} for s, c in results], ensure_ascii=False, indent=1))
        return
    for rank, (s, c) in enumerate(results, 1):
        print(f"#{rank} [{s:.1f}] {c['category']} | {c['heading'][:110]}")
        print(f"    docs/rag/blender-api/{c['path']}")
        body = c["text"].split("\n\n", 1)[-1]
        if args.full:
            print("\n" + body + "\n" + "-" * 80)
        else:
            snippet = " ".join(body.split())[:300]
            print(f"    {snippet}\n")


if __name__ == "__main__":
    main()
