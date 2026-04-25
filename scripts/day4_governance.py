from pathlib import Path
import json

import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


ROOT = Path(".")
SILVER = ROOT / "lakehouse/silver/employees.parquet"
RISK = ROOT / "lakehouse/gold/fact_attrition_risk.parquet"
METRICS = ROOT / "apps/api/models/day2_model_metrics.json"
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"
NOTEBOOKS = ROOT / "notebooks"

DOCS.mkdir(exist_ok=True)
IMAGES.mkdir(parents=True, exist_ok=True)
NOTEBOOKS.mkdir(exist_ok=True)


emp = pd.read_parquet(SILVER)
risk = pd.read_parquet(RISK)
df = emp.merge(risk, on="EmployeeID")

overall_high = (df["RiskBand"] == "High").mean()


def disparate_impact(group_col: str) -> pd.DataFrame:
    rows = []
    for group, sub in df.groupby(group_col):
        high_rate = (sub["RiskBand"] == "High").mean()
        rows.append(
            {
                "group_col": group_col,
                "group": group,
                "n": len(sub),
                "high_risk_rate": high_rate,
                "disparate_impact_ratio": high_rate / overall_high if overall_high else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values("disparate_impact_ratio")


gender_di = disparate_impact("Gender")
age_di = disparate_impact("AgeBand")
dept_di = disparate_impact("Department")

audit_table = pd.concat([gender_di, age_di, dept_di], ignore_index=True)
audit_table.to_csv(DOCS / "fairness_audit_summary.csv", index=False)

auc_rows = []
for group_col in ["Gender", "AgeBand", "Department"]:
    for group, sub in df.groupby(group_col):
        if sub["AttritionFlag"].nunique() > 1:
            auc_rows.append(
                {
                    "group_col": group_col,
                    "group": group,
                    "n": len(sub),
                    "roc_auc": roc_auc_score(sub["AttritionFlag"], sub["RiskScore"]),
                }
            )

auc_table = pd.DataFrame(auc_rows)
auc_table.to_csv(DOCS / "fairness_auc_by_group.csv", index=False)

plot_df = pd.concat([gender_di, age_di], ignore_index=True)
plot_df["label"] = plot_df["group_col"] + ": " + plot_df["group"].astype(str)

plt.figure(figsize=(10, 6))
plt.barh(plot_df["label"], plot_df["disparate_impact_ratio"])
plt.axvline(0.8, linestyle="--")
plt.axvline(1.25, linestyle="--")
plt.xlabel("Disparate impact ratio")
plt.ylabel("Group")
plt.title("Fairness audit — high-risk prediction rate by group")
plt.tight_layout()
plt.savefig(IMAGES / "fairness_audit.png", dpi=150, bbox_inches="tight")
plt.close()

metrics = json.loads(METRICS.read_text(encoding="utf-8")) if METRICS.exists() else {}
rf = metrics.get("models", {}).get("Random Forest", {})
report = metrics.get("random_forest_classification_report", {})

roc_auc = rf.get("roc_auc", "TBC")
pr_auc = rf.get("pr_auc", "TBC")

model_card = f"""# Model Card — Attrition Risk Model

## Intended use

This model is designed as decision support for HR Business Partners, people analytics teams, and CHRO-level reporting. It surfaces employees or employee groups with elevated attrition risk so that managers can review engagement, workload, career progression, and support signals.

The model must not be used as an automated decision maker.

## Out-of-scope use

- Automated termination, demotion, or negative performance decisions
- Individual pay decisions
- Surveillance or disciplinary monitoring
- Any use on real employee data without a fresh privacy, legal, and fairness review

## Training data

- Source: public IBM HR Analytics Employee Attrition dataset
- Rows: 1,470 employees
- Augmentations: synthetic monthly employee snapshots, synthetic recruitment funnel, synthetic engagement pulse
- No real employee data is used

## Model

- Architecture: Random Forest classifier
- Baseline comparison: Logistic Regression
- Target: `AttritionFlag`
- Output: `RiskScore`, `RiskBand`, and top SHAP risk drivers
- Risk table: `lakehouse/gold/fact_attrition_risk.parquet`

## Performance

- Random Forest ROC-AUC: {roc_auc}
- Random Forest PR-AUC: {pr_auc}
- Evaluation split: 25% holdout, stratified by attrition label

## Fairness review

Fairness checks were run across Gender, AgeBand, and Department.

The audit reports:
- High-risk prediction rate by group
- Disparate impact ratio by group
- ROC-AUC by group where both classes are present

See:
- `docs/fairness_audit_summary.csv`
- `docs/fairness_auc_by_group.csv`
- `docs/images/fairness_audit.png`
- `notebooks/05_fairness_audit.ipynb`

## Privacy and governance

- Anonymised employee IDs
- Bucketed age and salary attributes
- k-anonymity threshold recommended for demographic visuals
- Human-in-the-loop required for any intervention
- AI/Copilot calls are audit logged by the API

## Limitations

- Small public dataset, not a production HR dataset
- Static source data; time-series snapshots are synthetic
- Attrition reason is unknown
- Model should be retrained and re-audited before any real deployment
- Predictions should be used for supportive retention action only

## Recommended production controls

- Quarterly retraining
- Group-level fairness monitoring
- Row-level security in the semantic model
- Legal/privacy review before using real employee data
- Clear communication that risk scores are decision support, not decisions
"""

(DOCS / "model_card.md").write_text(model_card, encoding="utf-8")

nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell("# 05 — Fairness Audit\n\nThis notebook documents the fairness audit for the attrition risk model."),
    nbf.v4.new_code_cell("import pandas as pd\n\npd.read_csv('../docs/fairness_audit_summary.csv')"),
    nbf.v4.new_code_cell("pd.read_csv('../docs/fairness_auc_by_group.csv')"),
    nbf.v4.new_markdown_cell(
        "## Interpretation\n\n"
        "The fairness audit is used as a governance checkpoint, not as proof that the model is safe for production. "
        "In a real deployment, any group-level disparity would trigger a review before the model was used for HR intervention."
    ),
]
nbf.write(nb, NOTEBOOKS / "05_fairness_audit.ipynb")

print("Governance artefacts created:")
print(" - docs/model_card.md")
print(" - docs/fairness_audit_summary.csv")
print(" - docs/fairness_auc_by_group.csv")
print(" - docs/images/fairness_audit.png")
print(" - notebooks/05_fairness_audit.ipynb")
