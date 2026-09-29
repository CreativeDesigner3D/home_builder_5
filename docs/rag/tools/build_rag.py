#!/usr/bin/env python3
"""Build the BlenderToMob RAG corpus from the Blender Python API reference zip.

Reads the Sphinx HTML build (``blender_python_reference_5_2.zip``) directly from
the zip and produces, under ``docs/rag/blender-api/``:

- ``corpus/<page>.md``       one Markdown file per API page (links rewritten to .md)
- ``index/chunks.jsonl``     retrieval chunks (heading-aware, size-capped, link-free text)
- ``index/symbols.tsv``      every Python symbol from objects.inv -> corpus file#anchor
- ``index/pages.tsv``        page -> title, category, size
- ``index/manifest.json``    build metadata (Blender version, counts)

Usage:
    python3 docs/rag/tools/build_rag.py [path/to/blender_python_reference_5_2.zip]

Requires: beautifulsoup4, markdownify (pip install beautifulsoup4 markdownify).
"""

import json
import re
import sys
import zipfile
import zlib
from multiprocessing import Pool
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

try:
    import lxml  # noqa: F401
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "rag" / "blender-api"
DEFAULT_ZIP = ROOT / "blender_python_reference_5_2.zip"

SKIP_PREFIXES = ("genindex", "search", "py-modindex", "index")
CHUNK_MAX = 6000  # characters per chunk (~1.5k tokens)
CHUNK_MIN = 400


def category_of(page):
    """Coarse category used for filtering in rag_search.py."""
    if page.startswith("bpy_types_enum_items/"):
        return "enum_items"
    if page.startswith("info_") or page in ("change_log",):
        return "guide"
    parts = page.split(".")
    if parts[0] == "bpy" and len(parts) > 1:
        return "bpy." + parts[1]
    return parts[0]


class Converter(MarkdownConverter):
    """markdownify with Sphinx-aware tweaks (code blocks, signatures, links)."""

    def convert_a(self, el, text, *args, **kwargs):
        href = el.get("href", "")
        if "headerlink" in (el.get("class") or []):
            return ""
        if href and not re.match(r"^[a-z]+://", href):
            href = re.sub(r"\.html(?=$|#)", ".md", href)
            el["href"] = href
        return super().convert_a(el, text, *args, **kwargs)


def preprocess(article):
    """Rewrite Sphinx constructs into simpler HTML before markdownify."""
    soup = article
    for tag in soup.select("a.headerlink"):
        tag.decompose()

    # "Inherited Properties/Functions" tables repeat bpy_struct members on every
    # bpy.types page (~65% of its size). Collapse them to a plain list of names.
    for sec in soup.select('section[id^="inherited"]'):
        names = [" ".join(a.get_text().split()) for a in sec.select("td a, td code")]
        names = list(dict.fromkeys(n for n in names if n))
        for el in list(sec.children):
            if getattr(el, "name", None) not in ("h1", "h2", "h3", "h4"):
                el.extract()
        p = soup_new(sec, "p")
        p.string = ", ".join(names)
        sec.append(p)

    # Code blocks -> <pre data-lang> with plain text.
    for div in soup.select('div[class*="highlight-"]'):
        lang = "python"
        for c in div.get("class", []):
            if c.startswith("highlight-"):
                lang = {"python3": "python", "default": "python", "pycon": "pycon"}.get(c[10:], c[10:])
        pre = div.find("pre")
        code = pre.get_text() if pre else div.get_text()
        new = soup_new(div, "pre")
        new["data-lang"] = lang
        new.string = code
        div.replace_with(new)

    # Admonitions -> blockquote with bold title.
    for adm in soup.select("div.admonition"):
        title = adm.find(class_="admonition-title")
        label = title.get_text(strip=True) if title else "Note"
        if title:
            title.decompose()
        bq = soup_new(adm, "blockquote")
        strong = soup_new(adm, "p")
        strong.string = f"**{label}:**"
        bq.append(strong)
        for child in list(adm.children):
            bq.append(child.extract())
        adm.replace_with(bq)

    # Field lists (Type / Parameters / Returns) -> labelled paragraphs.
    for fl in soup.select("dl.field-list"):
        # Sphinx splits types into adjacent <em> runs ("*Callable**[**...") -- keep plain text.
        for em in fl.find_all("em"):
            em.unwrap()
        container = soup_new(fl, "div")
        for dt in fl.find_all("dt", recursive=False):
            dd = dt.find_next_sibling("dd")
            label = dt.get_text(strip=True).rstrip(":")
            p = soup_new(fl, "p")
            p.string = f"**{label}:**"
            container.append(p)
            if dd:
                for child in list(dd.children):
                    container.append(child.extract())
        fl.replace_with(container)

    # API definitions -> heading "<qualifier> <fully.qualified.name>(<params>)" with anchor.
    defs = [(dl, len(dl.find_parents("dl", class_="py"))) for dl in soup.select("dl.py")]
    for dl, depth in defs:
        dt = dl.find("dt", recursive=False)
        if not dt:
            continue
        anchor = dt.get("id", "")
        prop = dt.find(class_="property")
        qualifier = prop.get_text(" ", strip=True) + " " if prop else ""
        name_el = dt.find(class_="sig-name")
        name = name_el.get_text(strip=True) if name_el else ""
        params = ""
        if name_el:
            params = "".join(
                s.get_text() if hasattr(s, "get_text") else str(s) for s in name_el.next_siblings
            )
        params = " ".join(params.split()).replace("\u00b6", "")
        heading = soup_new(dl, f"h{min(3 + depth, 6)}")
        heading.string = f"{qualifier}{anchor or name}{params}".replace("`", "").strip()
        if anchor:
            heading["data-anchor"] = anchor
        dd = dl.find("dd", recursive=False)
        wrapper = soup_new(dl, "div")
        wrapper.append(heading)
        if dd:
            for child in list(dd.children):
                wrapper.append(child.extract())
        dl.replace_with(wrapper)
    return soup


def soup_new(el, name):
    root = el
    while root.parent is not None:
        root = root.parent
    return root.new_tag(name)


def html_to_md(html):
    soup = BeautifulSoup(html, PARSER)
    article = soup.find("article") or soup.find(attrs={"role": "main"}) or soup.body
    title_tag = article.find("h1")
    title = title_tag.get_text(" ", strip=True).replace("\u00b6", "").strip() if title_tag else ""
    preprocess(article)
    # Keep anchors: emit an <a id> marker before each API heading.
    for h in article.find_all(attrs={"data-anchor": True}):
        marker = soup.new_tag("span")
        marker.string = f"@@ANCHOR:{h['data-anchor']}@@"
        h.insert_before(marker)
    for sec in article.find_all("section"):
        if sec.get("id"):
            marker = soup.new_tag("span")
            marker.string = f"@@ANCHOR:{sec['id']}@@"
            sec.insert(0, marker)

    md = Converter(heading_style="ATX", bullets="-", code_language_callback=lambda el: el.get("data-lang", "python"),
                   escape_underscores=False, escape_asterisks=False).convert_soup(article)
    md = re.sub(r"@@ANCHOR:([^@]+)@@\s*", lambda m: f'\n<a id="{m.group(1)}"></a>\n\n', md)
    md = md.replace("¶", "")
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return title, md


LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')


def md_to_plain(md):
    text = LINK_RE.sub(r"\1", md)
    text = ANCHOR_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def chunk_page(page, title, category, md):
    """Split a page at headings, merging small sections and capping large ones."""
    lines = md.splitlines()
    sections = []  # (breadcrumb, anchor, symbols, text)
    crumbs = {}
    cur = {"heading": title, "anchor": "", "lines": [], "symbols": []}
    pending_anchor = ""
    in_code = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if in_code or line.lstrip().startswith("```"):
            cur["lines"].append(line)
            continue
        m = ANCHOR_RE.fullmatch(line.strip())
        if m:
            pending_anchor = m.group(1)
            if "." in pending_anchor and not pending_anchor.startswith(("module-", "rna-enum")):
                cur["symbols"].append(pending_anchor)
            continue
        h = re.match(r"^(#{1,6}) (.*)", line)
        if h and len(h.group(1)) <= 4:
            if cur["lines"]:
                sections.append(cur)
            level = len(h.group(1))
            crumbs[level] = h.group(2).strip()
            for k in list(crumbs):
                if k > level:
                    del crumbs[k]
            cur = {"heading": " > ".join(crumbs[k] for k in sorted(crumbs)), "anchor": pending_anchor,
                   "lines": [line], "symbols": [pending_anchor] if pending_anchor and "." in pending_anchor else []}
            pending_anchor = ""
            continue
        cur["lines"].append(line)
    if cur["lines"]:
        sections.append(cur)

    chunks = []
    buf = None
    for sec in sections:
        text = "\n".join(sec["lines"]).strip()
        if not text or sec["heading"].split(" > ")[-1].startswith("Inherited"):
            continue
        if buf and len(buf["text"]) + len(text) < CHUNK_MAX and (len(buf["text"]) < CHUNK_MIN or len(text) < CHUNK_MIN):
            buf["text"] += "\n\n" + text
            buf["symbols"] += sec["symbols"]
            continue
        if buf:
            chunks.append(buf)
        buf = {"heading": sec["heading"], "anchor": sec["anchor"], "text": text, "symbols": list(sec["symbols"])}
    if buf:
        chunks.append(buf)

    # Hard-split oversized chunks on paragraph boundaries.
    final = []
    for c in chunks:
        if len(c["text"]) <= CHUNK_MAX:
            final.append(c)
            continue
        part, n = [], 0
        for para in c["text"].split("\n\n"):
            if n + len(para) > CHUNK_MAX and part:
                final.append({**c, "text": "\n\n".join(part)})
                part, n = [], 0
            part.append(para)
            n += len(para) + 2
        if part:
            final.append({**c, "text": "\n\n".join(part)})

    out = []
    for i, c in enumerate(final):
        plain = md_to_plain(c["text"])
        if not plain:
            continue
        out.append({
            "id": f"{page}#{i}",
            "page": page,
            "title": title,
            "category": category,
            "heading": c["heading"],
            "anchor": c["anchor"],
            "symbols": sorted(set(c["symbols"]))[:200],
            "path": f"corpus/{page}.md" + (f"#{c['anchor']}" if c["anchor"] else ""),
            "text": f"[{title}] {c['heading']}\n\n{plain}",
        })
    return out


def read_inventory(data):
    header, _, rest = data.partition(b"# The remainder of this file is compressed using zlib.\n")
    meta = header.decode()
    text = zlib.decompress(rest).decode()
    rows = []
    for line in text.splitlines():
        m = re.match(r"(?x)(.+?)\s+(\S+:\S+)\s+(-?\d+)\s+(\S*)\s+(.*)", line)
        if not m:
            continue
        name, role, _prio, uri, _disp = m.groups()
        if uri.endswith("$"):
            uri = uri[:-1] + name
        page, _, anchor = uri.partition("#")
        rows.append((name, role, "corpus/" + re.sub(r"\.html$", ".md", page) + (f"#{anchor}" if anchor else "")))
    version = re.search(r"# Project: (.*)", meta)
    return rows, version.group(1) if version else "unknown"


_ZIP_CACHE = {}


def convert_page(job):
    """Worker: convert one HTML page from the zip and write its Markdown file."""
    zpath, prefix, name = job
    zf = _ZIP_CACHE.get(zpath) or _ZIP_CACHE.setdefault(zpath, zipfile.ZipFile(zpath))
    rel = name[len(prefix):]
    page = rel[:-5]
    title, md = html_to_md(zf.read(name).decode("utf-8"))
    cat = category_of(page)
    dest = OUT / "corpus" / f"{page}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = f"<!-- source: Blender Python API reference 5.2 / {rel} -->\n\n"
    dest.write_text(source + md, encoding="utf-8")
    return page, title, cat, len(md), chunk_page(page, title, cat, md)


def main():
    zpath = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ZIP
    zf = zipfile.ZipFile(zpath)
    prefix = zf.namelist()[0].split("/")[0] + "/"
    corpus = OUT / "corpus"
    index = OUT / "index"
    corpus.mkdir(parents=True, exist_ok=True)
    index.mkdir(parents=True, exist_ok=True)

    names = []
    for name in sorted(n for n in zf.namelist() if n.endswith(".html")):
        rel = name[len(prefix):]
        if "/.doctrees/" in name or rel.startswith(("_static", ".")):
            continue
        if rel[:-5].split("/")[-1].startswith(SKIP_PREFIXES):
            continue
        names.append(name)

    pages = []
    n_chunks = 0
    jobs = [(str(zpath), prefix, name) for name in names]
    with open(index / "chunks.jsonl", "w", encoding="utf-8") as fchunks, Pool() as pool:
        for i, (page, title, cat, size, chunks) in enumerate(pool.imap(convert_page, jobs, chunksize=4)):
            pages.append((page, title, cat, size))
            for ch in chunks:
                fchunks.write(json.dumps(ch, ensure_ascii=False) + "\n")
                n_chunks += 1
            if i % 250 == 0:
                print(f"  [{i}/{len(jobs)}] {page}", flush=True)

    rows, version = read_inventory(zf.read(prefix + "objects.inv"))
    with open(index / "symbols.tsv", "w", encoding="utf-8") as f:
        f.write("symbol\trole\tpath\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    with open(index / "pages.tsv", "w", encoding="utf-8") as f:
        f.write("page\ttitle\tcategory\tchars\n")
        for p in sorted(pages):
            f.write("\t".join(map(str, p)) + "\n")
    cats = {}
    for p in pages:
        cats[p[2]] = cats.get(p[2], 0) + 1
    manifest = {
        "source": zpath.name,
        "blender_api": version,
        "pages": len(pages),
        "chunks": n_chunks,
        "symbols": len(rows),
        "categories": dict(sorted(cats.items(), key=lambda kv: -kv[1])),
        "chunk_max_chars": CHUNK_MAX,
    }
    (index / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
