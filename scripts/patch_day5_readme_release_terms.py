from pathlib import Path

p = Path("README.md")
s = p.read_text(encoding="utf-8")

capabilities_section = """
## AI Copilot capabilities

| Capability | What it does |
|---|---|
| Board narrative generation | Converts KPI inputs into a short CHRO-ready executive story |
| Policy Q&A | Answers HR policy questions using the local policy corpus |
| Attrition risk explanation | Explains model risk drivers in plain English |
| Audit logging | Records Copilot usage for governance review |
| Human-in-the-loop framing | Keeps employee-level risk as decision support, not automation |
"""

release_section = """
## Release

Current baseline release:

```text
v1-polished
```

This release represents the polished v1 baseline: lakehouse, ML risk model, Power BI report, governance docs, local API smoke test, and Streamlit smoke test.
"""

insert = ""

if "AI Copilot capabilities" not in s:
    insert += capabilities_section + "\n"

if "v1-polished" not in s:
    insert += release_section + "\n"

if insert:
    if "</div>" in s:
        s = s.replace("</div>", insert + "\n</div>")
    else:
        s = s.rstrip() + "\n\n" + insert

p.write_text(s, encoding="utf-8")
print("README patched for v1 release verification.")
