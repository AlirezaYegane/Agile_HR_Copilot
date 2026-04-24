from pathlib import Path
import json
import pandas as pd

required = [
    "lakehouse/gold/fact_attrition_risk.parquet",
    "docs/images/shap_summary.png",
    "apps/api/models/attrition_rf.joblib",
    "apps/api/models/attrition_logit.joblib",
    "apps/api/models/feature_meta.joblib",
    "apps/api/models/shap_explainer.joblib",
    "apps/api/models/day2_model_metrics.json",
    "notebooks/04_ml_attrition.ipynb",
]

missing = [p for p in required if not Path(p).exists()]
if missing:
    print("Missing Day 2 files:")
    for p in missing:
        print(" -", p)
    raise SystemExit(1)

risk = pd.read_parquet("lakehouse/gold/fact_attrition_risk.parquet")
metrics = json.loads(Path("apps/api/models/day2_model_metrics.json").read_text())

expected_cols = {
    "EmployeeID",
    "RiskScore",
    "RiskBand",
    "TopDriver1",
    "TopDriver1Impact",
    "TopDriver2",
    "TopDriver2Impact",
    "TopDriver3",
    "TopDriver3Impact",
}

missing_cols = expected_cols - set(risk.columns)
if missing_cols:
    print("Missing columns in fact_attrition_risk:")
    print(missing_cols)
    raise SystemExit(1)

if len(risk) != 1470:
    print(f"Expected 1,470 risk rows, got {len(risk):,}")
    raise SystemExit(1)

rf_auc = metrics["models"]["Random Forest"]["roc_auc"]
logit_auc = metrics["models"]["Logistic Regression"]["roc_auc"]

print("DAY 2 VERIFY PASSED")
print(f"risk rows: {len(risk):,}")
print("risk bands:")
print(risk["RiskBand"].value_counts().to_string())
print(f"random forest ROC-AUC: {rf_auc:.3f}")
print(f"logistic ROC-AUC: {logit_auc:.3f}")
print("files ready for Power BI:")
for p in sorted(Path("lakehouse/gold").glob("*.parquet")):
    print(" -", p.name)
