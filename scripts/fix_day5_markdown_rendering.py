from pathlib import Path
import re

files = [
    Path("README.md"),
    Path("docs/architecture.md"),
    Path("docs/model_card.md"),
    Path("docs/release_notes_v1.md"),
]

for p in files:
    if not p.exists():
        continue

    s = p.read_text(encoding="utf-8")

    # Remove accidental code fence ids like ```mermaid id="abc"
    s = re.sub(r"```([a-zA-Z0-9_-]+)\s+id=\"[^\"]+\"", r"```\1", s)

    # Remove accidental plain text code fence ids like ```text id="abc"
    s = re.sub(r"```text\s+id=\"[^\"]+\"", "```text", s)
    s = re.sub(r"```powershell\s+id=\"[^\"]+\"", "```powershell", s)

    # Make docs explicitly left-to-right for GitHub/Markdown preview
    if not s.lstrip().startswith('<div dir="ltr">'):
        s = '<div dir="ltr">\n\n' + s.strip() + '\n\n</div>\n'

    p.write_text(s, encoding="utf-8")
    print(f"fixed {p}")
