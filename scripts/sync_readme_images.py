from pathlib import Path
import re

readme_path = Path("README.md")
text = readme_path.read_text(encoding="utf-8", errors="ignore")

replacement = """## Screenshots

### AI Copilot

| Board Narrative | Policy Q&A | Risk Explanation |
|---|---|---|
| ![Copilot Narrative](docs/images/copilot_narrative.png) | ![Copilot Q&A](docs/images/copilot_qa.png) | ![Copilot Risk](docs/images/copilot_risk.png) |

### Model explainability and governance

| SHAP Summary | Fairness Audit |
|---|---|
| ![SHAP summary](docs/images/shap_summary.png) | ![Fairness audit](docs/images/fairness_audit.png) |

### Power BI dashboards

The Power BI report is available at:

`powerbi/AgileHRCopilot.pbix`

Dashboard screenshots will be added after final visual polish:

- Executive Overview
- Attrition & Retention
- Employee Engagement
- Diversity & Inclusion
- Workforce Planning
"""

# Replace the existing screenshots/dashboard screenshot block if it exists.
patterns = [
    r"## Dashboard screenshots.*?(?=\n## |\Z)",
    r"## Screenshots.*?(?=\n## |\Z)",
]

updated = text
for pattern in patterns:
    if re.search(pattern, updated, flags=re.S):
        updated = re.sub(pattern, replacement + "\n\n", updated, flags=re.S)
        break
else:
    updated += "\n\n" + replacement + "\n"

readme_path.write_text(updated, encoding="utf-8")
print("README screenshot section synced.")
