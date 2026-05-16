from __future__ import annotations

import json
from pathlib import Path


def exists_any(paths: list[str]) -> bool:
    return any(Path(p).exists() for p in paths)


required_exact = [
    "README.md",
    "docs/architecture.md",
    "docs/model_card.md",
    "docs/release_notes_v1.md",
    "docs/demo_questions.md",
    "docs/images/shap_summary.png",
    "docs/images/fairness_audit.png",
    "artifacts/day5/api_smoke_report.json",
    "artifacts/day5/streamlit_smoke_report.json",
    "scripts/smoke_day5_api.py",
]

required_groups = {
    "Power BI page 1 executive screenshot": [
        "docs/images/page1_executive.png",
    ],
    "Power BI page 2 attrition screenshot": [
        "docs/images/page2_attrition.png",
    ],
    "Power BI page 3 engagement screenshot": [
        "docs/images/page3_engagement.png",
        "docs/images/page3_attrition_detail.png",
    ],
    "Power BI page 4 diversity screenshot": [
        "docs/images/page4_diversity.png",
        "docs/images/page4_engagement.png",
    ],
    "Power BI page 5 workforce screenshot": [
        "docs/images/page5_workforce.png",
        "docs/images/page5_diversity.png",
    ],
    "Copilot hero or narrative screenshot": [
        "docs/images/copilot_hero.png",
        "docs/images/copilot_narrative.png",
        "docs/images/copilot_qa.png",
    ],
    "Power BI PBIX": [
        "powerbi/AgileHRCopilot.pbix",
    ],
}

missing: list[str] = []

for p in required_exact:
    if not Path(p).exists():
        missing.append(p)

for label, paths in required_groups.items():
    if not exists_any(paths):
        missing.append(f"{label}: one of {paths}")

if missing:
    print("V1 RELEASE VERIFY FAILED")
    print("Missing:")
    for item in missing:
        print(" -", item)
    raise SystemExit(1)

api_report = json.loads(Path("artifacts/day5/api_smoke_report.json").read_text(encoding="utf-8"))
streamlit_report = json.loads(
    Path("artifacts/day5/streamlit_smoke_report.json").read_text(encoding="utf-8")
)

api_checks = api_report.get("checks", {})
required_api_checks = ["health", "narrative", "ask", "explain_risk"]

missing_api = [x for x in required_api_checks if x not in api_checks]
if missing_api:
    print("V1 RELEASE VERIFY FAILED")
    print("Missing API smoke checks:", missing_api)
    raise SystemExit(1)

if not streamlit_report.get("streamlit_ready"):
    print("V1 RELEASE VERIFY FAILED")
    print("Streamlit smoke report does not show streamlit_ready=true")
    raise SystemExit(1)

readme = Path("README.md").read_text(encoding="utf-8")
required_readme_terms = [
    "Agile HR Copilot",
    "AI Copilot capabilities",
    "Governance",
    "v1-polished",
    "docs/architecture.md",
    "docs/model_card.md",
]

missing_terms = [x for x in required_readme_terms if x not in readme]
if missing_terms:
    print("V1 RELEASE VERIFY FAILED")
    print("README missing expected terms:", missing_terms)
    raise SystemExit(1)

print("V1 RELEASE VERIFY PASSED")
print("API checks:", ", ".join(api_checks.keys()))
print("Streamlit ready:", streamlit_report.get("streamlit_ready"))
print("README/docs/screenshots present.")
