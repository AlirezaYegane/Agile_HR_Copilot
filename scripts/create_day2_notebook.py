from pathlib import Path
import nbformat as nbf

NOTEBOOKS = Path("notebooks")
NOTEBOOKS.mkdir(exist_ok=True)

nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell(
        "# 04 — ML Attrition Risk\n\n"
        "This notebook documents the Day 2 attrition-risk modelling workflow for Agile HR Copilot."
    ),
    nbf.v4.new_markdown_cell(
        "## Objective\n\n"
        "Train an attrition-risk model using the Day 1 silver employee table, generate SHAP explanations, "
        "and write employee-level risk scores back into the gold layer as `fact_attrition_risk.parquet`."
    ),
    nbf.v4.new_markdown_cell(
        "## Implementation\n\n"
        "The reproducible implementation lives in:\n\n"
        "`scripts/day2_train_attrition_model.py`\n\n"
        "It trains Logistic Regression and Random Forest models, evaluates ROC-AUC and PR-AUC, saves "
        "`docs/images/shap_summary.png`, writes `lakehouse/gold/fact_attrition_risk.parquet`, and stores "
        "model artefacts under `apps/api/models/`."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\n"
        "import json\n"
        "import pandas as pd\n\n"
        "metrics_path = Path('../apps/api/models/day2_model_metrics.json')\n"
        "risk_path = Path('../lakehouse/gold/fact_attrition_risk.parquet')\n\n"
        "print(metrics_path.exists(), risk_path.exists())\n"
    ),
    nbf.v4.new_code_cell(
        "metrics = json.loads(metrics_path.read_text())\n"
        "metrics['models']"
    ),
    nbf.v4.new_code_cell(
        "risk = pd.read_parquet(risk_path)\n"
        "risk.head()"
    ),
    nbf.v4.new_markdown_cell(
        "## Notes for interview\n\n"
        "- The model is decision support, not a decision maker.\n"
        "- SHAP is used to explain risk drivers in plain language.\n"
        "- The risk table is written back to the gold layer so Power BI can consume it as part of the semantic model."
    ),
]

nbf.write(nb, NOTEBOOKS / "04_ml_attrition.ipynb")
print("Created notebooks/04_ml_attrition.ipynb")
