#!/usr/bin/env python3
"""Build a print-ready book of Paul Graham essays.

    python3 build.py                      # paperback (default)
    python3 build.py --cover 13.92x10.25  # exact cover size Lulu shows you, in inches
    python3 build.py --refetch            # ignore the download cache

Outputs land in out/:
    interior.pdf   6x9in book block (6.25x9.25in pages incl. bleed) for Lulu
    cover.pdf      full wraparound cover (back + spine + front, with bleed)
    cover.png, cover-front.png   previews
    ORDER.md       the exact settings to pick on Lulu for this build

The essay selection and the order of parts live in essays.json.
Requires: python3 with beautifulsoup4, and typst (brew install typst).
"""
import argparse
import html as htmlmod
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:
    raise SystemExit("Missing dependency: run  pip3 install beautifulsoup4")

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
BUILD = ROOT / "build"
OUT = ROOT / "out"
BASE = "https://paulgraham.com/"
UA = "Mozilla/5.0 (personal book build)"

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

# sentinels used while flattening HTML into paragraphs
PB, BR, BLK, REF = "\x01", "\x02", "\x03", "\x04"


# ---------------------------------------------------------------- fetching
def fetch(name, refetch=False):
    CACHE.mkdir(exist_ok=True)
    path = CACHE / name
    if path.exists() and not refetch:
        return path.read_text(encoding="latin-1")
    req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=30).read()
    path.write_bytes(data)
    time.sleep(0.4)  # be polite
    return data.decode("latin-1")


def essay_titles(refetch):
    idx = fetch("articles.html", refetch)
    titles = {}
    for slug, t in re.findall(r'<a href="([a-z0-9_]+)\.html">(.*?)</a>', idx):
        t = htmlmod.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        if t:
            titles.setdefault(slug, re.sub(r"\s+", " ", t))
    return titles


# ---------------------------------------------------------------- typst escaping
def esc(text):
    """Escape plain text for Typst markup."""
    text = re.sub(r"[\\#$*_`<>@\[\]~/]", lambda m: "\\" + m.group(0), text)
    return text


def tstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "    ") + '"'


def dashes(text):
    # PG types em dashes as "--" with irregular spacing
    text = re.sub(r"\s*(--+|\u2014)\s*", "\u2014", text)
    return text


# ---------------------------------------------------------------- html -> typst
class Converter:
    def __init__(self):
        self.blocks = []

    def block(self, typ):
        self.blocks.append(typ)
        return f"{PB}{BLK}{len(self.blocks) - 1}{BLK}{PB}"

    def text(self, s):
        s = dashes(s)
        out = []
        pos = 0
        for m in re.finditer(r"\[(\d{1,2})\]", s):  # older essays: plain [1] markers
            out.append(esc(s[pos:m.start()]))
            out.append(f"{REF}{m.group(1)}{REF}")
            pos = m.end()
        out.append(esc(s[pos:]))
        return "".join(out)

    def walk(self, node):
        if isinstance(node, NavigableString):
            if node.__class__.__name__ in ("Comment", "Doctype", "Declaration"):
                return ""
            return self.text(str(node))
        if not isinstance(node, Tag):
            return ""
        name = node.name
        if name in ("script", "style", "map", "title", "head", "form"):
            return ""
        if name in ("img", "hr", "input"):
            return self.children(node)  # html.parser sometimes nests text inside void tags
        if name == "table" and len(node.get_text()) < 1500:
            return ""  # translation links, YC banners, layout spacers
        if name == "nref":
            return f"{REF}{node.get('n')}{REF}"
        if name == "br":
            return BR + self.children(node)
        if name in ("pre", "xmp") or (name == "font" and "courier" in (node.get("face") or "").lower()
                                       and "\n" in node.get_text()):
            code = node.get_text().strip("\n").expandtabs(4)
            return self.block(f"#codeblock({tstr(code)})")
        if name == "code":
            return "#raw(" + tstr(node.get_text()) + ")"
        if name == "blockquote":
            inner = self.paragraphs(self.children(node))
            return self.block("#blockquote[\n" + "\n\n".join(inner) + "\n]")
        if name in ("ul", "ol"):
            items = []
            # html.parser nests unclosed <li> tags inside each other; flatten them
            for li in node.find_all("li"):
                inner = "".join(self.walk(ch) for ch in li.children if not (isinstance(ch, Tag) and ch.name == "li"))
                items.append("[" + " ".join(self.paragraphs(inner)) + "]")
            fn = "enum" if name == "ol" else "list"
            return self.block(f"#{fn}(" + ", ".join(items) + ")") if items else ""
        inner = self.children(node)
        if name in ("i", "em", "cite"):
            return f"#emph[{inner}]" if inner.strip() and PB not in inner and BR * 2 not in inner else inner
        if name in ("b", "strong"):
            return f"#strong[{inner}]" if inner.strip() and PB not in inner and BR * 2 not in inner else inner
        if name in ("p", "center", "div", "h1", "h2", "h3", "h4"):
            return PB + inner + PB
        return inner

    def children(self, node):
        return "".join(self.walk(c) for c in node.children)

    def paragraphs(self, s):
        s = re.sub(BR + r"\s*(" + BR + r"\s*)+", PB, s)
        paras = []
        for p in s.split(PB):
            p = re.sub(r"\s+", " ", p).strip()
            p = re.sub(r"\s*" + BR + r"\s*", " #linebreak() ", p).strip()
            p = re.sub(r"^(#linebreak\(\) )+|( #linebreak\(\))+$", "", p).strip()
            p = re.sub(REF + r"(\d+)" + REF, r"#nref(\1)", p)
            p = re.sub(r"\s+(#nref\()", r"\1", p)  # glue ref to preceding word
            if re.match(r"^(\d+\.|[-+=])", p):
                p = "\\" + p if not p[0].isdigit() else re.sub(r"^(\d+)\.", r"\1\\.", p)
            if p:
                paras.append(p)
        return paras


def prepare(raw):
    # footnote markers in the body: [<a href="#f1n">1</a>], often wrapped in a grey <font>
    raw = re.sub(r'<font[^>]*>\s*\[\s*<a href="#f(\d+)n"[^>]*>.*?</a>\s*\]\s*</font>', r'<nref n="\1"></nref>', raw, flags=re.S | re.I)
    raw = re.sub(r'\[\s*<a href="#f(\d+)n"[^>]*>.*?</a>\s*\]', r'<nref n="\1"></nref>', raw, flags=re.S | re.I)
    # footnote anchors in the notes section
    raw = re.sub(r'\[\s*<a name="f(\d+)n"[^>]*>.*?</a>\s*\]', r'<nref n="\1"></nref>', raw, flags=re.S | re.I)
    return raw


def convert(raw, slug, title):
    soup = BeautifulSoup(prepare(raw), "html.parser")
    fonts = [f for f in soup.find_all("font") if "verdana" in (f.get("face") or "").lower()]
    if not fonts:
        raise SystemExit(f"{slug}: could not find essay body")
    body = max(fonts, key=lambda f: len(f.get_text()))
    conv = Converter()
    paras = conv.paragraphs(conv.children(body))

    def expand(p):
        return re.sub(BLK + r"(\d+)" + BLK, lambda m: conv.blocks[int(m.group(1))], p)

    date = ""
    if paras and len(paras[0]) < 60 and re.match(rf"({MONTHS}) \d{{4}}", paras[0]):
        date = paras.pop(0)

    main, notes, thanks = [], [], []
    section = "main"
    for p in paras:
        plain = re.sub(r"#strong\[(.*?)\]", r"\1", p).strip()
        if section == "main" and plain.rstrip(":") == "Notes":
            section = "notes"
            continue
        if re.match(r"^(#strong\[)?Thanks(\])? ", p) or re.match(r"^#emph\[Thanks", p):
            thanks.append(re.sub(r"^#strong\[Thanks\]", "Thanks", p))
            section = "thanks"
            continue
        if section == "main":
            if re.fullmatch(r"#strong\[[^\[\]]*\]", p):
                p = "#subhead" + p[len("#strong"):]
            main.append(p)
        elif section == "notes":
            m = re.match(r"^#nref\((\d+)\)\s*(.*)$", p)
            if m:
                notes.append([m.group(1), m.group(2)])
            elif notes:
                notes[-1][1] += "\n\n" + p
            else:
                notes.append(["", p])
        else:
            thanks.append(p)

    # small-caps lead-in on the first words of the essay
    for i, p in enumerate(main):
        if p.startswith("#") or BLK in p:
            break
        words = p.split(" ")
        lead = []
        for w in words[:5]:
            if re.fullmatch(r"[A-Za-z'’\-]+", w):
                lead.append(w)
            else:
                break
        if len(lead) >= 2 or (lead and len(words) > 1):
            n = max(1, min(len(lead), 4 if len(lead) >= 4 else len(lead)))
            main[i] = "#leadin[" + " ".join(words[:n]) + "] " + " ".join(words[n:])
        break

    year = re.search(r"\d{4}", date).group(0) if date else ""
    out = ['#import "/style.typ": *', f"#essay(title: {tstr(title)}, date: {tstr(date)}, slug: {tstr(slug)})[",
           "\n\n".join(expand(p) for p in main), "]"]
    if notes:
        out.append("#endnotes(")
        for n, txt in notes:
            out.append(f"  ({tstr(n)}, [{expand(txt)}]),")
        out.append(")")
    if thanks:
        out.append("#thanks[" + " ".join(expand(t) for t in thanks) + "]")
    words = len(re.sub(r"#\w+(\(.*?\))?|[\[\]\\]", " ", "\n".join(main)).split())
    return "\n".join(out) + "\n", year, words


# ---------------------------------------------------------------- main
def typst(*args):
    try:
        r = subprocess.run(["typst", *args, "--root", str(ROOT)], cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit("Missing dependency: install Typst (macOS: brew install typst; "
                         "others: https://github.com/typst/typst#installation)")
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit(f"typst {' '.join(args[:2])} failed")
    if r.stderr.strip():
        sys.stderr.write(r.stderr)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--cover", metavar="WxH",
                    help="exact cover size Lulu asks for, in inches, e.g. 13.41x9.25 "
                         "(default: paperback size from Lulu's spine formula)")
    ap.add_argument("--no-cover", action="store_true")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "essays.json").read_text())
    titles = essay_titles(a.refetch)
    (BUILD / "essays").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)

    content = ['#import "/style.typ": *']
    years, total_words, count = [], 0, 0
    part_titles = []
    for pi, part in enumerate(cfg["parts"]):
        num = "" if part.get("unnumbered") else ROMAN[pi]
        first = ", first: true" if pi == 0 else ""
        content.append(f'#part({tstr(num)}, {tstr(part["title"])}{first})')
        part_titles.append({"num": num, "title": part["title"], "essays": [titles[s] for s in part["essays"]]})
        for slug in part["essays"]:
            if slug not in titles:
                raise SystemExit(f"unknown essay: {slug}")
            raw = fetch(slug + ".html", a.refetch)
            typ, year, words = convert(raw, slug, titles[slug])
            (BUILD / "essays" / f"{slug}.typ").write_text(typ)
            content.append(f'#include "essays/{slug}.typ"')
            if year:
                years.append(int(year))
            total_words += words
            count += 1
            print(f"  {ROMAN[pi]:>4}  {titles[slug]:<45} {year:>5} {words:>7,} words")
    (BUILD / "content.typ").write_text("\n".join(content) + "\n")
    meta = {"title": cfg["title"], "author": cfg["author"], "count": count,
            "first": min(years), "last": max(years),
            "parts": part_titles}
    (BUILD / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\n{count} essays, ~{total_words:,} words, {meta['first']}\u2013{meta['last']}")

    typst("compile", "book.typ", str(OUT / "interior.pdf"))
    pages = int(json.loads(typst("query", "book.typ", "<total-pages>", "--field", "value", "--one")))
    print(f"interior: {pages} pages -> out/interior.pdf")

    if a.no_cover:
        return
    if a.cover:
        try:
            cw, ch = (float(v) for v in a.cover.lower().replace("in", "").split("x"))
        except ValueError:
            raise SystemExit("--cover must look like 13.41x9.25 (width x height in inches)")
        edge = (ch - 9) / 2               # bleed (paperback) or wrap (hardcover) per edge
        spine = cw - 12 - 2 * edge
        if not (0 < edge < 2 and 0 < spine < 4):
            raise SystemExit(f"--cover {a.cover} doesn't look like a 6x9 cover for this book")
    else:
        edge = 0.125
        spine = pages / 444 + 0.06       # Lulu's paperback spine formula
        cw, ch = 12 + spine + 2 * edge, 9 + 2 * edge
    inputs = ["--input", f"spine={spine:.4f}", "--input", f"edge={edge:.4f}"]
    typst("compile", "cover.typ", str(OUT / "cover.pdf"), *inputs)
    typst("compile", "cover.typ", str(OUT / "cover.png"), "--ppi", "110", *inputs)
    typst("compile", "cover.typ", str(OUT / "cover-front.png"), "--ppi", "200", "--input", "front=1", *inputs)
    print(f"cover: {cw:.3f} x {ch:.3f} in (spine {spine:.3f} in) -> out/cover.pdf")
    write_order_sheet(meta, pages, cw, ch, spine, custom=bool(a.cover))


def write_order_sheet(meta, pages, cw, ch, spine, custom):
    kind = "the size you passed with --cover" if custom else "paperback, from Lulu's spine formula"
    sheet = f"""# Order sheet for this build

Generated by build.py. Use these exact values on lulu.com.

| Setting | Value |
|---|---|
| Goal | **Print Copies for Your Own Use** (personal printing: no ISBN, not for sale) |
| Title | **{meta['title']}** (must match the files) |
| Author / contributor | {meta['author']} |
| Interior file | `out/interior.pdf` ({pages} pages, 6.25 x 9.25 in incl. bleed) |
| Book size | **US Trade, 6 x 9 in** |
| Page count | **{pages}** (Lulu reads this from the PDF) |
| Interior color | **Standard Black & White** |
| Paper | **60# Cream, Uncoated** |
| Binding | **Paperback Perfect Bound** or **Hardcover Case Wrap** |
| Cover finish | **Matte** |
| Cover file | `out/cover.pdf`, built at **{cw:.3f} x {ch:.3f} in** ({kind}) |

The cover file must match the cover size Lulu shows after you upload the
interior (Design step, under "Upload Your Cover"). If it doesn't, or if you
choose hardcover, rebuild the cover with Lulu's number and upload again:

    python3 build.py --cover WIDTHxHEIGHT

Spine width in this build: {spine:.3f} in.
"""
    (OUT / "ORDER.md").write_text(sheet)
    print("order sheet -> out/ORDER.md")

if __name__ == "__main__":
    main()
