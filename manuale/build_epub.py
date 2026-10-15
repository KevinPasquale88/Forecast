#!/usr/bin/env python3
"""Assemble the EPUB source: replace ```mermaid fences with PNG images (raster, not PDF —
PDF images are not reliably supported by EPUB readers), swap the LaTeX-only front matter
files for plain-Markdown equivalents, and concatenate everything without the \\newpage
page-break commands the PDF build uses (meaningless, and left as stray text, in reflowable
EPUB)."""
import re
import os

MANUALE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(MANUALE_DIR)

DIAGRAM_MAP = {
    "cap_02.md": ["diagrams/cap_02_fig1.png"],
    "cap_03.md": ["diagrams/cap_03_fig1.png"],
    "cap_12.md": ["diagrams/cap_12_fig1.png"],
    "cap_17.md": ["diagrams/cap_17_fig1.png"],
    "cap_18.md": ["diagrams/cap_18_fig1.png"],
    "cap_54.md": ["diagrams/cap_54_fig1.png"],
}

def replace_mermaid(fname, content):
    if fname not in DIAGRAM_MAP:
        return content
    images = iter(DIAGRAM_MAP[fname])
    def _sub(match):
        try:
            img = next(images)
        except StopIteration:
            return match.group(0)
        return f"![]({img})"
    return re.sub(r"```mermaid\n.*?```", _sub, content, flags=re.DOTALL)

def fix_math_for_mathml(content):
    """pandoc 2.12's bundled texmath can't convert \\tag{...} (equation numbering) or
    \\operatorname*{...}_{...} (starred operatorname with a subscript) to MathML — both
    render fine for the LaTeX/Tectonic PDF build, but for EPUB they'd fall back to raw,
    unreadable TeX source text. The equation number is already given in the surrounding
    prose ("Formula N.N"), so dropping \\tag here loses nothing; \\operatorname*{arg\\,max}
    becomes \\mathop{\\mathrm{arg\\,max}}\\limits, which texmath converts correctly."""
    content = re.sub(r"\s*\\tag\{[^}]*\}", "", content)
    content = re.sub(r"\\operatorname\*\{arg\\,max\}_\{", r"\\mathop{\\mathrm{arg\\,max}}\\limits_{", content)
    return content

def main():
    nums = [f"cap_{i:02d}.md" for i in range(59)]
    apps = [f"app_{c}.md" for c in "ABCDEF"]
    order = ["cap_00a_copertina_epub.md", "cap_00b_elenchi_epub.md"] + nums + apps

    out_parts = []
    for fname in order:
        with open(fname, encoding="utf-8") as f:
            content = f.read()
        content = replace_mermaid(fname, content)
        content = fix_math_for_mathml(content)
        out_parts.append(content)

    combined = "\n\n".join(out_parts)
    with open("_combined_epub.md", "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Wrote _combined_epub.md ({len(combined)} chars, {len(order)} source files)")

if __name__ == "__main__":
    main()
