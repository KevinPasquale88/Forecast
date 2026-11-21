"""Costruisce manuale_v2/Forecast_Manuale_Tesi_v2.epub in Python puro (nessun pandoc).

Requisiti:  pip install markdown latex2mathml pandas
Eseguire:   python manuale_v2/build_epub.py   (da qualunque cartella)

Passi: unisce i capitoli in ordine, inserisce l'Appendice C generata da genera_tabelle.py,
converte le formule ```latex in MathML, divide il testo in un file XHTML per parte e per
capitolo, scrive indice (nav.xhtml + toc.ncx), manifest e archivio EPUB 3.
"""
import datetime
import glob
import html
import os
import re
import sys
import uuid
import zipfile

import markdown
from latex2mathml.converter import convert as latex_to_mathml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from genera_tabelle import build as appendice_c  # noqa: E402

TITLE = "Forecast — Manuale per la tesi"
SUBTITLE = "Seconda edizione: pipeline corretta, risultati, chatbot e discussione"
DATE = "2026-11-14"
OUT = os.path.join(HERE, "Forecast_Manuale_Tesi_v2.epub")


def formulas_to_mathml(text):
    def repl(m):
        tex = m.group(1).strip()
        try:
            mml = latex_to_mathml(tex, display="block")
            return f'\n<div class="formula">{mml}</div>\n'
        except Exception:
            return f"\n<pre>{html.escape(tex)}</pre>\n"
    return re.sub(r"```latex\n(.*?)\n```", repl, text, flags=re.S)


def split_chunks(text):
    """Un blocco per ogni titolo '# ' (parte) o '## ' (capitolo), ignorando i blocchi di codice."""
    chunks, current, in_code = [], [], False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code and (line.startswith("# ") or line.startswith("## ")) and current:
            if any(l.strip() for l in current):
                chunks.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def figures(body):
    """<p><img alt="x" src="y" /></p>  ->  <figure> con didascalia."""
    return re.sub(
        r'<p><img alt="([^"]*)" src="([^"]*)" /></p>',
        lambda m: f'<figure><img alt="{m.group(1)}" src="{m.group(2)}" /><figcaption>{m.group(1)}</figcaption></figure>',
        body,
    )


def xhtml(title, body):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="it" lang="it">
<head><meta charset="utf-8" /><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="epub.css" /></head>
<body>
{body}
</body>
</html>
"""


def main():
    files = sorted(glob.glob(os.path.join(HERE, "capitoli", "*.md")))
    text = "\n\n".join(open(f, encoding="utf-8").read() for f in files)
    text = text.replace("<!-- APPENDICE_C -->", appendice_c())
    text = formulas_to_mathml(text)

    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"], output_format="xhtml")
    docs, toc = [], []  # toc: (livello, titolo, file)
    for i, chunk in enumerate(split_chunks(text), start=1):
        first = chunk.splitlines()[0]
        level = 1 if first.startswith("# ") else 2
        title = first.lstrip("#").strip().replace("`", "")
        name = f"sez_{i:03d}.xhtml"
        body = figures(md.reset().convert(chunk))
        docs.append((name, title, xhtml(title, body)))
        toc.append((level, title, name))

    images = sorted(glob.glob(os.path.join(HERE, "figure", "*.png")))
    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'forecast-manuale-tesi-v2')}"
    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    title_page = xhtml(TITLE, f'<section class="titolo"><h1>{html.escape(TITLE)}</h1>'
                              f'<p class="sottotitolo">{html.escape(SUBTITLE)}</p>'
                              f'<p class="data">14 novembre 2026</p></section>')

    # nav.xhtml (EPUB 3) con parti e capitoli annidati
    nav_items, open_part = [], False
    for level, title, name in toc:
        link = f'<a href="{name}">{html.escape(title)}</a>'
        if level == 1:
            if open_part:
                nav_items.append("</ol></li>")
            nav_items.append(f"<li>{link}<ol>")
            open_part = True
        else:
            nav_items.append(f"<li>{link}</li>")
    if open_part:
        nav_items.append("</ol></li>")
    nav_body = "".join(nav_items).replace("<ol></ol>", "")
    nav = xhtml("Indice", f'<nav epub:type="toc" id="toc"><h1>Indice</h1><ol>{nav_body}</ol></nav>')

    # toc.ncx (compatibilità con lettori EPUB 2)
    points, n = [], 0
    for level, title, name in toc:
        n += 1
        points.append(f'<navPoint id="p{n}" playOrder="{n}"><navLabel><text>{html.escape(title)}</text></navLabel>'
                      f'<content src="{name}"/></navPoint>')
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{book_id}"/></head>
<docTitle><text>{html.escape(TITLE)}</text></docTitle><navMap>{''.join(points)}</navMap></ncx>
"""

    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
                '<item id="css" href="epub.css" media-type="text/css"/>',
                '<item id="titolo" href="titolo.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="titolo"/>', '<itemref idref="nav"/>']
    for name, _, content in docs:
        props = ' properties="mathml"' if "<math" in content else ""
        manifest.append(f'<item id="{name[:-6]}" href="{name}" media-type="application/xhtml+xml"{props}/>')
        spine.append(f'<itemref idref="{name[:-6]}"/>')
    for j, img in enumerate(images):
        manifest.append(f'<item id="img{j}" href="figure/{os.path.basename(img)}" media-type="image/png"/>')

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="it">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{book_id}</dc:identifier>
<dc:title>{html.escape(TITLE)}</dc:title>
<dc:language>it</dc:language>
<dc:date>{DATE}</dc:date>
<dc:description>{html.escape(SUBTITLE)}</dc:description>
<meta property="dcterms:modified">{modified}</meta>
</metadata>
<manifest>{''.join(manifest)}</manifest>
<spine toc="ncx">{''.join(spine)}</spine>
</package>
"""
    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    with zipfile.ZipFile(OUT, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/titolo.xhtml", title_page, compress_type=zipfile.ZIP_DEFLATED)
        z.write(os.path.join(HERE, "epub.css"), "OEBPS/epub.css", compress_type=zipfile.ZIP_DEFLATED)
        for name, _, content in docs:
            z.writestr(f"OEBPS/{name}", content, compress_type=zipfile.ZIP_DEFLATED)
        for img in images:
            z.write(img, f"OEBPS/figure/{os.path.basename(img)}", compress_type=zipfile.ZIP_DEFLATED)
    words = len(re.sub(r"<[^>]+>", " ", text).split())
    print(f"Scritto {OUT}: {len(docs)} sezioni, {len(images)} figure, circa {words} parole, "
          f"{os.path.getsize(OUT) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
