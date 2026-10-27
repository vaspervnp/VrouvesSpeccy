#!/usr/bin/env python3
"""docs/MANUAL.md and docs/MANUAL_GR.md -> PDF (A4), next to them.

    pip install markdown weasyprint
    tools/manual_images.py      # pictures in docs/img (after make)
    tools/make_manual.py        # or: make manuals
"""
import os

import markdown
from weasyprint import HTML

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
        @bottom-center { content: counter(page); font-size: 9pt; color: #666; } }
body { font-family: "Noto Sans", "DejaVu Sans", sans-serif; font-size: 10.5pt;
       line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 26pt; color: #0b3d91; margin: 0 0 2mm 0; letter-spacing: 0.5pt; }
h1 + p em { color: #555; font-size: 12pt; }
h2 { font-size: 15pt; color: #0b3d91; border-bottom: 2px solid #f0a020;
     padding-bottom: 1mm; margin-top: 7mm; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
img { image-rendering: pixelated; }
p > img { display: block; width: 100%; margin: 2mm 0 4mm 0; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm 0; font-size: 9.5pt;
        page-break-inside: auto; }
tr { page-break-inside: avoid; }
th { background: #0b3d91; color: white; text-align: left; padding: 1.5mm 2mm; }
td { border-bottom: 1px solid #ccc; padding: 1.5mm 2mm; vertical-align: middle; }
p > img[src^="img/stage"] { width: 80%; margin: 2mm auto 4mm auto; }
td img { height: 13mm; width: auto; display: block; }
pre { background: #111; color: #ffd84a; padding: 3mm 4mm; font-size: 11pt; border-radius: 1mm; }
code { font-family: "Noto Sans Mono", "DejaVu Sans Mono", monospace; }
.stage { page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #ccc; margin-top: 8mm; }
"""


def build(name):
    md = open(os.path.join(DOCS, name + ".md"), encoding="utf-8").read()
    body = markdown.markdown(md, extensions=["tables", "fenced_code", "md_in_html"])
    lang = "el" if name.endswith("_GR") else "en"
    html = ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><style>%s</style>'
            '</head><body>%s</body></html>' % (lang, CSS, body))
    out = os.path.join(DOCS, name + ".pdf")
    HTML(string=html, base_url=DOCS).write_pdf(out)
    print(out)


if __name__ == "__main__":
    for n in ("MANUAL", "MANUAL_GR"):
        build(n)
