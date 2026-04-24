from pathlib import Path
import json
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


warnings.filterwarnings("ignore", category=UserWarning)

SILVER = Path("lakehouse/silver/employees.parquet")
GOLD = Path("lakehouse/gold")
IMAGES = Path("docs/images")
MODEL_DIR = Path("apps/api/models")
NOTEBOOKS = Path("notebooks")

IMAGES.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOKS.mkdir(parents=True, exist_ok=True)


def clean_feature_name(name: str) -> str:
    name = name.replace("num__", "")
    name = name.replace("cat__", "")
    return name


def top_drivers(shap_row: np.ndarray, feature_names: np.ndarray, k: int = 3) -> list[tuple[str, float]]:
    idx = np.argsort(np.abs(shap_row))[::-1][:k]
    return [(clean_feature_name(str(feature_names[i])), float(shap_row[i])) for i in idx]


def choose_threshold(y_true: pd.Series, proba: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, proba)

    # F1 over available thresholds; precision/recall arrays are one item longer.
    f1 = (2 * precision[:-1] * recall[:-1]) / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    best_idx = int(np.nanargmax(f1))

    return float(thresholds[best_idx])


def main() -> None:
    if not SILVER.exists():
        raise FileNotFoundError(f"Missing {SILVER}. Run Day 1 first.")

    df = pd.read_parquet(SILVER)

    target = "AttritionFlag"
    drop_cols = [
        "EmployeeID",
        "Attrition",
        "AttritionFlag",
        "_ingest_ts",
        "_source",
        "_row_hash",
    ]
    drop_cols = [c for c in drop_cols if c in df.columns]

    X = df.drop(columns=drop_cols)
    y = df[target]

    cat_cols = X.select_dtypes(include=["object", "string"]).columns.tolist()
    num_cols = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()

    print("DAY 2 ML TRAINING")
    print(f"rows: {len(df):,}")
    print(f"numeric features: {len(num_cols)}")
    print(f"categorical features: {len(cat_cols)}")
    print(f"target rate: {y.mean():.3f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=42,
    )

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )

    logit = Pipeline(
        steps=[
            ("pre", pre),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    rf = Pipeline(
        steps=[
            ("pre", pre),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=8,
                    class_weight="balanced",
                    n_jobs=-1,
                    random_state=42,
                ),
            ),
        ]
    )

    print("\nTraining Logistic Regression...")
    logit.fit(X_train, y_train)

    print("Training Random Forest...")
    rf.fit(X_train, y_train)

    results = {}
    for name, model in [("Logistic Regression", logit), ("Random Forest", rf)]:
        proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, proba)
        pr_auc = average_precision_score(y_test, proba)
        results[name] = {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
        }
        print(f"{name:20s} ROC-AUC={roc_auc:.3f} | PR-AUC={pr_auc:.3f}")

    rf_proba = rf.predict_proba(X_test)[:, 1]
    threshold = choose_threshold(y_test, rf_proba)
    pred = (rf_proba >= threshold).astype(int)

    print(f"\nChosen threshold: {threshold:.3f}")
    print("\nClassification report:")
    print(classification_report(y_test, pred, digits=3))

    cm = pd.DataFrame(
        confusion_matrix(y_test, pred),
        index=["Actual Stay", "Actual Leave"],
        columns=["Pred Stay", "Pred Leave"],
    )
    print("\nConfusion matrix:")
    print(cm)

    print("\nComputing SHAP...")
    rf_fitted = rf.named_steps["clf"]
    pre_fitted = rf.named_steps["pre"]

    X_test_tx = pre_fitted.transform(X_test)
    feature_names = pre_fitted.get_feature_names_out()

    explainer = shap.TreeExplainer(rf_fitted)

    sample_size = min(300, X_test_tx.shape[0])
    sample_idx = np.random.RandomState(42).choice(X_test_tx.shape[0], sample_size, replace=False)
    shap_values = explainer.shap_values(X_test_tx[sample_idx])

    if isinstance(shap_values, list):
        sv_sample = shap_values[1]
    else:
        sv_sample = shap_values[:, :, 1] if shap_values.ndim == 3 else shap_values

    plt.figure(figsize=(9, 6))
    shap.summary_plot(
        sv_sample,
        X_test_tx[sample_idx],
        feature_names=feature_names,
        show=False,
        max_display=15,
    )
    plt.tight_layout()
    shap_path = IMAGES / "shap_summary.png"
    plt.savefig(shap_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved SHAP summary: {shap_path}")

    print("\nScoring all employees...")
    full_proba = rf.predict_proba(X)[:, 1]
    X_full_tx = pre_fitted.transform(X)
    sv_all_raw = explainer.shap_values(X_full_tx)

    if isinstance(sv_all_raw, list):
        sv_all = sv_all_raw[1]
    else:
        sv_all = sv_all_raw[:, :, 1] if sv_all_raw.ndim == 3 else sv_all_raw

    risk_rows = []
    for i, emp_id in enumerate(df["EmployeeID"].values):
        drivers = top_drivers(sv_all[i], feature_names, k=3)
        score = float(full_proba[i])

        risk_rows.append(
            {
                "EmployeeID": emp_id,
                "RiskScore": score,
                "RiskBand": "High" if score >= 0.50 else ("Medium" if score >= 0.25 else "Low"),
                "TopDriver1": drivers[0][0],
                "TopDriver1Impact": drivers[0][1],
                "TopDriver2": drivers[1][0],
                "TopDriver2Impact": drivers[1][1],
                "TopDriver3": drivers[2][0],
                "TopDriver3Impact": drivers[2][1],
            }
        )

    fact_risk = pd.DataFrame(risk_rows)
    risk_path = GOLD / "fact_attrition_risk.parquet"
    fact_risk.to_parquet(risk_path, engine="pyarrow", compression="snappy", index=False)

    print(f"Saved risk fact: {risk_path}")
    print("\nRisk distribution:")
    print(fact_risk["RiskBand"].value_counts())

    model_metrics = {
        "rows": int(len(df)),
        "target_rate": float(y.mean()),
        "threshold": threshold,
        "models": results,
        "random_forest_classification_report": classification_report(y_test, pred, digits=3, output_dict=True),
        "confusion_matrix": cm.to_dict(),
        "feature_counts": {
            "numeric": len(num_cols),
            "categorical": len(cat_cols),
            "transformed": int(len(feature_names)),
        },
    }

    metrics_path = MODEL_DIR / "day2_model_metrics.json"
    metrics_path.write_text(json.dumps(model_metrics, indent=2), encoding="utf-8")

    joblib.dump(rf, MODEL_DIR / "attrition_rf.joblib")
    joblib.dump(logit, MODEL_DIR / "attrition_logit.joblib")
    joblib.dump(
        {
            "feature_names": [str(x) for x in feature_names],
            "num_cols": num_cols,
            "cat_cols": cat_cols,
            "threshold": threshold,
        },
        MODEL_DIR / "feature_meta.joblib",
    )

    # SHAP explainer can be large/noisy across versions, but useful for Day 3 if needed.
    joblib.dump(explainer, MODEL_DIR / "shap_explainer.joblib")

    print(f"\nSaved metrics: {metrics_path}")
    print("Saved model artefacts under apps/api/models/")
    print("\nDAY 2 ML COMPLETE")


if __name__ == "__main__":
    main()
