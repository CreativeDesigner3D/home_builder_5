#!/usr/bin/env python3
"""Gera o RAG do Manual de Treinamento Promob (docs/rag/promob/) a partir do PDF.

Requer apenas Python 3 (stdlib) e `pdftotext` (poppler-utils).

Saída:
    docs/rag/promob/corpus/NN-<capitulo>.md   1 arquivo por capítulo, seções como títulos Markdown e marcadores de página
    docs/rag/promob/index/chunks.jsonl        1 chunk por seção (≤ 6000 caracteres), pronto para busca/embedding
    docs/rag/promob/index/toc.tsv             sumário: número, título, parte, página, arquivo#âncora
    docs/rag/promob/index/manifest.json       metadados do build

O corpus e o índice reproduzem o texto do manual (material proprietário da Promob) e ficam fora do git
(docs/rag/promob/.gitignore); só o gerador, a busca e o README são versionados.

Uso:
    python3 docs/rag/tools/build_promob_rag.py [--pdf manual-treinamento-promob.pdf]
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "rag" / "promob"
MAX_CHUNK = 6000

TOC_ENTRY_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.+?)\s*(?:\.\s)+\.?\s*(\d+)\s*$")
TOC_PART_RE = re.compile(r"^\s*([^\d\s.*][^.]*?)\s{3,}(\d+)\s*$")
FOOTER_RE = re.compile(r"^\s*(\d+\s+-\s.*-|-\s.*-\s+\d+)\s*$")
CHAPTER_RE = re.compile(r"^\s*C\s?APÍTULO\s+\d+\s*$")
LIST_RE = re.compile(r"^(\d+\.|[a-z]\)|[ivx]+\)|[•●◦▪-])\s")


def slug(text):
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-")


def extract_pages(pdf):
    res = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True)
    text = unicodedata.normalize("NFKC", res.stdout)  # desfaz ligaduras (ﬁ → fi) do LaTeX
    return text.split("\f")  # índice i = página i+1 do PDF (= página impressa)


def parse_toc(pages):
    toc_text = "\n".join(pages[2:17])
    entries, part = [], None
    for line in toc_text.splitlines():
        m = TOC_ENTRY_RE.match(line)
        if m:
            num, title, page = m.groups()
            entries.append(dict(num=num, title=re.sub(r"\s+", " ", title), page=int(page), part=part))
            continue
        m = TOC_PART_RE.match(line)
        if m and m.group(1).strip() not in ("Sumário",):
            part = m.group(1).strip()
    return entries


def clean_page(text):
    lines = [ln for ln in text.splitlines() if not FOOTER_RE.match(ln)]
    return lines


def locate_headings(pages, entries):
    """Acha cada entrada do sumário no corpo: (página, linha). Busca a partir da página indicada."""
    found = []
    for e in entries:
        words = [re.escape(w) for w in e["title"].split()]
        pat = re.compile(r"^\s*" + re.escape(e["num"]) + r"\s+" + r"\s+".join(words) + r"\s*$")
        hit = None
        for p in range(e["page"] - 1, min(e["page"] + 2, len(pages))):
            for li, ln in enumerate(clean_page(pages[p])):
                if pat.match(ln):
                    hit = (p, li)
                    break
            if hit:
                break
        if hit is None and "." not in e["num"]:
            hit = (e["page"] - 1, 0)  # capítulo: título aparece como "C APÍTULO N" + nome
        if hit:
            found.append(dict(e, pidx=hit[0], line=hit[1]))
    found.sort(key=lambda h: (h["pidx"], h["line"]))
    return found


def reflow(lines):
    """Junta linhas quebradas pelo layout em parágrafos; preserva itens de lista e linhas em branco."""
    out, para = [], []

    def flush():
        if para:
            out.append(" ".join(para))
            para.clear()

    for raw in lines:
        s = raw.strip()
        if not s or CHAPTER_RE.match(raw):
            flush()
            if out and out[-1] != "":
                out.append("")
            continue
        if LIST_RE.match(s):
            flush()
        para.append(s)
    flush()
    text = "\n".join(out).strip()
    text = re.sub(r"(\w)- (\w)", r"\1\2", text)  # hifenização de fim de linha
    return re.sub(r"\n{3,}", "\n\n", text)


def section_text(pages, start, end):
    """Texto entre o título `start` (exclusive) e o título `end` (exclusive), com marcadores de página."""
    chunks = []
    last_p = end["pidx"] if end else len(pages) - 1
    for p in range(start["pidx"], last_p + 1):
        lines = clean_page(pages[p])
        a = start["line"] + 1 if p == start["pidx"] else 0
        b = end["line"] if (end and p == end["pidx"]) else len(lines)
        if p == start["pidx"] and "." not in start["num"]:
            a = 0  # capítulo: pula "C APÍTULO N" e o nome, que viram o título
            while a < len(lines) and (not lines[a].strip() or CHAPTER_RE.match(lines[a])
                                      or lines[a].strip() == start["title"]):
                a += 1
        body = reflow(lines[a:b])
        if body:
            chunks.append((p + 1, body))
    return chunks


def split_long(text, limit=MAX_CHUNK):
    if len(text) <= limit:
        return [text]
    parts, cur = [], ""
    for para in text.split("\n\n"):
        if cur and len(cur) + len(para) + 2 > limit:
            parts.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        parts.append(cur)
    return parts


def build(pdf):
    pages = extract_pages(pdf)
    entries = parse_toc(pages)
    heads = locate_headings(pages, entries)
    missing = [e["num"] for e in entries if e["num"] not in {h["num"] for h in heads}]

    corpus, index = OUT / "corpus", OUT / "index"
    corpus.mkdir(parents=True, exist_ok=True)
    index.mkdir(parents=True, exist_ok=True)
    for old in corpus.glob("*.md"):
        old.unlink()

    chapters = {}
    for h in heads:
        chapters.setdefault(h["num"].split(".")[0], []).append(h)

    titles = {h["num"]: h["title"] for h in heads}
    chunk_rows, toc_rows = [], []
    for i, h in enumerate(heads):
        nxt = heads[i + 1] if i + 1 < len(heads) else None
        chap = h["num"].split(".")[0]
        chap_title = titles.get(chap, "")
        fname = f"{int(chap):02d}-{slug(chap_title)}.md"
        anchor = slug(f"{h['num']} {h['title']}")
        crumbs = [h["part"] or ""] + [f"{'.'.join(h['num'].split('.')[:d])} {titles.get('.'.join(h['num'].split('.')[:d]), '')}"
                                      for d in range(1, h["num"].count(".") + 2)]
        crumb = " > ".join(c for c in crumbs if c.strip())
        body = section_text(pages, h, nxt)
        h["body"] = body
        h["file"], h["anchor"] = fname, anchor
        toc_rows.append(f"{h['num']}\t{h['title']}\t{h['part'] or ''}\t{h['page']}\tcorpus/{fname}#{anchor}")
        text = "\n\n".join(b for _, b in body)
        pages_span = sorted({p for p, _ in body}) or [h["page"]]
        for j, piece in enumerate(split_long(text)):
            if not piece.strip():
                continue
            chunk_rows.append(dict(
                id=f"{h['num']}#{j}", num=h["num"], title=h["title"], chapter=chap, chapter_title=chap_title,
                part=h["part"], heading=crumb, pages=[pages_span[0], pages_span[-1]],
                path=f"corpus/{fname}#{anchor}", text=f"[{crumb}] {piece}"))

    for chap, hs in chapters.items():
        chap_title = titles.get(chap, "")
        fname = f"{int(chap):02d}-{slug(chap_title)}.md"
        md = [f"# {chap} {chap_title}", "",
              f"> Manual de Treinamento Promob (V-1.17.1, 2016) — parte **{hs[0]['part']}**, "
              f"páginas {hs[0]['page']}–{hs[-1]['page']}. Texto extraído do PDF; figuras não incluídas.", ""]
        for h in hs:
            if "." in h["num"]:
                level = min(h["num"].count(".") + 1, 6)
                md += [f"{'#' * level} {h['num']} {h['title']}", ""]
            for p, b in h["body"]:
                md += [f"<!-- p. {p} -->", b, ""]
        (corpus / fname).write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    with open(index / "chunks.jsonl", "w", encoding="utf-8") as fh:
        for row in chunk_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    (index / "toc.tsv").write_text("num\ttitle\tpart\tpage\tpath\n" + "\n".join(toc_rows) + "\n", encoding="utf-8")
    manifest = dict(
        source=pdf.name, sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(), pages=len(pages) - 1,
        built=datetime.datetime.now().isoformat(timespec="seconds"), toc_entries=len(entries),
        headings_found=len(heads), headings_missing=missing, chapters=len(chapters), chunks=len(chunk_rows))
    (index / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / ".gitignore").write_text("# Texto do manual Promob (proprietário): não versionar\ncorpus/\nindex/\n",
                                    encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", default=str(ROOT / "manual-treinamento-promob.pdf"))
    args = ap.parse_args()
    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"PDF não encontrado: {pdf}")
    m = build(pdf)
    print(json.dumps({k: v for k, v in m.items() if k != "headings_missing"}, ensure_ascii=False))
    if m["headings_missing"]:
        print(f"títulos não localizados no corpo ({len(m['headings_missing'])}): {' '.join(m['headings_missing'])}")


if __name__ == "__main__":
    main()
