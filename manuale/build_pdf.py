#!/usr/bin/env python3
"""Assemble the full book: replace ```mermaid fences with rendered PDF images, concatenate in order."""
import re
import os

MANUALE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(MANUALE_DIR)

DIAGRAM_MAP = {
    "cap_02.md": ["diagrams/cap_02_fig1.pdf"],
    "cap_03.md": ["diagrams/cap_03_fig1.pdf"],
    "cap_12.md": ["diagrams/cap_12_fig1.pdf"],
    "cap_17.md": ["diagrams/cap_17_fig1.pdf"],
    "cap_18.md": ["diagrams/cap_18_fig1.pdf"],
    "cap_54.md": ["diagrams/cap_54_fig1.pdf"],
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
        return f"![]({img}){{ width=90% }}"
    return re.sub(r"```mermaid\n.*?```", _sub, content, flags=re.DOTALL)

def main():
    nums = [f"cap_{i:02d}.md" for i in range(59)]
    apps = [f"app_{c}.md" for c in "ABCDEF"]
    order = ["cap_00a_copertina.md", "cap_00b_elenchi.md"] + nums + apps

    out_parts = []
    for fname in order:
        with open(fname, encoding="utf-8") as f:
            content = f.read()
        content = replace_mermaid(fname, content)
        out_parts.append(content)
        out_parts.append("\n\n\\newpage\n\n")

    combined = "\n\n".join(out_parts)
    with open("_combined.md", "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Wrote _combined.md ({len(combined)} chars, {len(order)} source files)")

if __name__ == "__main__":
    main()
