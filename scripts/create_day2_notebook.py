"""
Regenerate notebooks/04_ml_attrition.ipynb from the polished source-of-truth content.
"""
from pathlib import Path
import nbformat as nbf

NOTEBOOKS = Path("notebooks")
NOTEBOOKS.mkdir(exist_ok=True)


nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(
        "# 04 — ML Attrition Risk\n\n"
        "**Layer:** Gold (writes back) · **Day:** 2 · "
        "**Authoritative script:** `scripts/day2_train_attrition_model.py`\n\n"
        "## Objective\n\n"
        "Train an attrition-risk model on the silver employee table, evaluate it, generate SHAP explanations, "
        "and write per-employee risk scores back to the gold layer so Power BI and the FastAPI Copilot can consume them.\n\n"
        "## Inputs\n\n"
        "- `lakehouse/silver/employees.parquet`\n\n"
        "## Outputs\n\n"
        "- `lakehouse/gold/fact_attrition_risk.parquet` — `EmployeeID`, `RiskScore`, `RiskBand`, top-3 SHAP drivers (signed)\n"
        "- `apps/api/models/attrition_rf.joblib`, `attrition_logit.joblib`, `feature_meta.joblib`, `shap_explainer.joblib`\n"
        "- `apps/api/models/day2_model_metrics.json`\n"
        "- `docs/images/shap_summary.png`\n\n"
        "## Approach\n\n"
        "1. Stratified 75/25 train/test on `AttritionFlag`.\n"
        "2. `ColumnTransformer(StandardScaler + OneHotEncoder)` → classifier.\n"
        "3. Random Forest (primary) + Logistic Regression (interpretable baseline).\n"
        "4. F1-optimal threshold from the precision-recall curve.\n"
        "5. Risk bands: `Low < 0.25 ≤ Medium < 0.50 ≤ High`.\n"
        "6. `shap.TreeExplainer` on the fitted RF; top-3 signed contributions per employee written to the risk table.\n\n"
        "## Business value\n\n"
        "The model is **decision support**: it gives HR Business Partners a ranked list and a plain-English "
        "explanation of why each employee is ranked where they are. That bridge from model to language is the product."
    ),
    nbf.v4.new_markdown_cell(
        "## Reproduce\n\n"
        "```powershell\n"
        "python scripts\\day2_train_attrition_model.py\n"
        "python scripts\\verify_day2.py\n"
        "```"
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\n"
        "import json\n"
        "import pandas as pd\n\n"
        "METRICS = Path('../apps/api/models/day2_model_metrics.json')\n"
        "RISK = Path('../lakehouse/gold/fact_attrition_risk.parquet')\n"
        "print('metrics exist:', METRICS.exists())\n"
        "print('risk fact exist:', RISK.exists())"
    ),
    nbf.v4.new_code_cell(
        "if METRICS.exists():\n"
        "    metrics = json.loads(METRICS.read_text())\n"
        "    for name, vals in metrics['models'].items():\n"
        "        print(f\"  {name:<22}  ROC-AUC={vals['roc_auc']:.3f}  PR-AUC={vals['pr_auc']:.3f}\")\n"
        "    print(f\"\\nF1-optimal threshold: {metrics['threshold']:.3f}\")"
    ),
    nbf.v4.new_code_cell(
        "if RISK.exists():\n"
        "    risk = pd.read_parquet(RISK)\n"
        "    print('rows:', len(risk))\n"
        "    print('\\nrisk band distribution:')\n"
        "    print(risk['RiskBand'].value_counts())\n"
        "    cols = ['EmployeeID','RiskScore','RiskBand','TopDriver1','TopDriver2','TopDriver3']\n"
        "    risk.sort_values('RiskScore', ascending=False)[cols].head(10)"
    ),
    nbf.v4.new_markdown_cell(
        "## Limitations (read with the model card)\n\n"
        "- Source is the small public IBM dataset; class balance is fixed.\n"
        "- Time-series snapshots are synthetic — temporal validation is **not** performed.\n"
        "- Attrition reason is unknown; the model only sees the flag.\n"
        "- The fairness audit (Notebook 05) is the governance gate before any deployment talk."
    ),
    nbf.v4.new_markdown_cell(
        "## Interview talking points\n\n"
        "- **Why two models** — the Logistic Regression baseline keeps stakeholders honest about the marginal value of the Random Forest.\n"
        "- **Why F1-optimal threshold** — the default 0.5 wastes signal on an imbalanced target.\n"
        "- **Why SHAP** — the per-employee top-3 drivers are what the Copilot actually narrates to a manager."
    ),
]

nbf.write(nb, NOTEBOOKS / "04_ml_attrition.ipynb")
print("Created notebooks/04_ml_attrition.ipynb")
