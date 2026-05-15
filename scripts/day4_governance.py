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

def _fmt_metric(value):
    if isinstance(value, (int, float)):
        return f"{value:.3f}"
    return value


roc_auc = _fmt_metric(rf.get("roc_auc", "TBC"))
pr_auc = _fmt_metric(rf.get("pr_auc", "TBC"))

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
    nbf.v4.new_markdown_cell(
        "# 05 — Fairness Audit\n\n"
        "**Layer:** Governance · **Day:** 4 · "
        "**Authoritative script:** `scripts/day4_governance.py`\n\n"
        "## Objective\n\n"
        "Document the model's **group-level behaviour** so a CHRO or risk committee can decide whether and how to deploy it. "
        "This is a governance checkpoint — not a deployment approval.\n\n"
        "## Inputs\n\n"
        "- `lakehouse/silver/employees.parquet`\n"
        "- `lakehouse/gold/fact_attrition_risk.parquet`\n\n"
        "## Outputs\n\n"
        "- `docs/fairness_audit_summary.csv`\n"
        "- `docs/fairness_auc_by_group.csv`\n"
        "- `docs/images/fairness_audit.png`\n"
        "- `docs/model_card.md`\n\n"
        "## Method\n\n"
        "1. Compute the overall high-risk rate.\n"
        "2. For each diagnostic group (`Gender`, `AgeBand`, `Department`): per-group high-risk rate "
        "and disparate-impact ratio = group rate / overall rate.\n"
        "3. Where both classes are present, compute per-group ROC-AUC.\n"
        "4. Render the disparate-impact bar with reference lines at 0.8 and 1.25."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\n"
        "import pandas as pd\n\n"
        "DOCS = Path('../docs')\n"
        "summary = DOCS / 'fairness_audit_summary.csv'\n"
        "auc = DOCS / 'fairness_auc_by_group.csv'\n"
        "print('summary exists:', summary.exists())\n"
        "print('auc exists:', auc.exists())"
    ),
    nbf.v4.new_code_cell(
        "if summary.exists():\n"
        "    df = pd.read_csv(summary)\n"
        "    df['disparate_impact_ratio'] = df['disparate_impact_ratio'].round(3)\n"
        "    df['high_risk_rate'] = df['high_risk_rate'].round(3)\n"
        "    df.sort_values('disparate_impact_ratio')"
    ),
    nbf.v4.new_code_cell(
        "if auc.exists():\n"
        "    pd.read_csv(auc).round(3)"
    ),
    nbf.v4.new_markdown_cell(
        "## Interpretation\n\n"
        "- The audit is **diagnostic, not normative**. It cannot tell you whether the model is fair; it tells you where to look.\n"
        "- The 0.8 / 1.25 thresholds come from EEOC \"four-fifths\" practice — pragmatic, not statutory.\n"
        "- Per-group AUC degradation is often more revealing than disparate-impact ratios on small samples.\n\n"
        "In a real deployment, any flagged group triggers (1) a data-quality and labelling check, "
        "(2) a feature-importance review for that cohort, and (3) a deploy / re-threshold / restrict / do-not-deploy decision."
    ),
    nbf.v4.new_markdown_cell(
        "## Interview talking points\n\n"
        "- The notebook is intentionally short — it is the **artefact**, not the analysis.\n"
        "- The CSVs and PNG are the outputs that go into the model-review pack.\n"
        "- `docs/model_card.md` is regenerated by the same script so the audit, metrics, and model description never drift."
    ),
]
nbf.write(nb, NOTEBOOKS / "05_fairness_audit.ipynb")

print("Governance artefacts created:")
print(" - docs/model_card.md")
print(" - docs/fairness_audit_summary.csv")
print(" - docs/fairness_auc_by_group.csv")
print(" - docs/images/fairness_audit.png")
print(" - notebooks/05_fairness_audit.ipynb")
