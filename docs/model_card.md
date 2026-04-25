# Model Card — Attrition Risk Model

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

- Random Forest ROC-AUC: 0.7859689539794855
- Random Forest PR-AUC: 0.44956128922161603
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
