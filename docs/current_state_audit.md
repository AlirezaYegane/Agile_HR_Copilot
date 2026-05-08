# Current State Audit — Agile HR Copilot

Date: 2026-05-08  
Project path: `D:\Agile_HR_Copilot`  
Branch: `main`  
Python: `3.11.9` from `.venv`

## 1. Repository status

The repository is functional but currently has uncommitted local changes.

Latest known HEAD:

- `81f3712 feat(powerbi): add workforce marts for stable planning dashboard`

Current git status includes modified documentation, notebooks, scripts, and the Power BI file, plus several untracked Power BI helper files and new data-generation scripts.

## 2. Verification scripts

| Check | Result | Notes |
|---|---:|---|
| `python scripts\verify_day1.py` | PASS | Bronze, silver, and gold lakehouse outputs exist. |
| `python scripts\verify_day2.py` | PASS | Attrition risk model outputs and Power BI-ready gold files exist. |
| `python scripts\verify_day4.py` | PASS | Governance/docs checks pass, but Power BI screenshots are missing. |

## 3. Data layer

| Artefact | Status | Notes |
|---|---:|---|
| Bronze layer | PASS | `1,470` rows. |
| Silver layer | PASS | `1,470` rows. |
| Employee monthly snapshot | PASS | `32,428` rows. |
| Gold star schema | PASS | Core facts/dimensions exist. |
| Additional marts | PASS | Workforce and recruitment marts exist. |

Gold files currently available:

- `dim_date.parquet`
- `dim_department.parquet`
- `dim_employee.parquet`
- `dim_jobrole.parquet`
- `fact_attrition_risk.parquet`
- `fact_employee_snapshot.parquet`
- `fact_engagement_pulse.parquet`
- `fact_pulse_themes.parquet`
- `fact_recruitment.parquet`
- `fact_recruitment_stage.parquet`
- `mart_recruitment_funnel.parquet`
- `mart_requisition_detail.parquet`
- `mart_role_level_inventory.parquet`
- `mart_workforce_kpis.parquet`
- `mart_workforce_monthly.parquet`

## 4. Machine learning layer

| Artefact | Status | Notes |
|---|---:|---|
| Logistic Regression | PASS | ROC-AUC: `0.829`. |
| Random Forest | PASS | ROC-AUC: `0.786`. |
| Risk fact table | PASS | `1,470` employee risk rows. |
| Risk bands | PASS | Low: `1068`, Medium: `207`, High: `195`. |
| SHAP summary | PASS | `docs/images/shap_summary.png` exists. |
| Saved model artefacts | PASS | RF, Logistic, SHAP explainer, feature metadata, and metrics JSON exist. |

## 5. Policy / RAG layer

| Artefact | Status | Notes |
|---|---:|---|
| Policy markdown files | PASS | 3 policy `.md` files exist. |
| Policy PDFs | PASS | 3 policy PDFs exist. |
| RAG index readiness | PASS | `/api/health` returned `rag_ready: true`. |
| Policy chunks | PASS | `/api/health` returned `policy_chunks: 12`. |

Policy files:

- `retention_career_growth.pdf`
- `compensation_pay_equity.pdf`
- `diversity_inclusion_wellbeing.pdf`

## 6. API / Copilot backend

| Endpoint | Status | Notes |
|---|---:|---|
| `/api/health` | PASS | Returned `status: ok`, `rag_ready: true`, `policy_chunks: 12`. |
| `/api/narrative` | PASS WITH FALLBACK | Endpoint works, but local fallback narrative was used because Gemini was unavailable. |
| `/api/ask` | PASS | Returned answer with policy sources. |
| `/api/explain-risk` | PASS | Returned explanation for high-risk employee `EMP_6D7ADA7D8E`. |

Example risk explanation test:

- Employee: `EMP_6D7ADA7D8E`
- Risk score: `93.5%`
- Risk band: `High`
- Top drivers: `MonthlyIncome`, `OverTime_Yes`, `TotalExperienceYears`

## 7. Streamlit UI

| Component | Status | Notes |
|---|---:|---|
| `apps/web/streamlit_app.py` | PASS | File exists. |
| Streamlit launch | PASS | App responded with HTTP `200`. |
| API dependency | PASS | API was started successfully before UI smoke test. |
| UI visual review | NOT FULLY REVIEWED | Smoke test confirms the app starts, but visual polish still needs manual review. |

Streamlit local URL:

- `http://127.0.0.1:8501`

## 8. Power BI report

| Artefact | Status | Notes |
|---|---:|---|
| `powerbi/AgileHRCopilot.pbix` | EXISTS | File exists and has local modifications. |
| Theme JSON | EXISTS / UNTRACKED | `powerbi/AgileHRTheme.json` exists but is currently untracked. |
| DAX guide | EXISTS / UNTRACKED | `powerbi/dax_measures.md` exists but is currently untracked. |
| Import guide | EXISTS / UNTRACKED | `powerbi/power_query_import_guide.md` exists but is currently untracked. |
| Page checklist | EXISTS / UNTRACKED | `powerbi/page_build_checklist.md` exists but is currently untracked. |
| Validation helper | EXISTS / UNTRACKED | `powerbi/validate_gold_for_powerbi.py` exists but is currently untracked. |

Power BI screenshots are currently missing:

- `docs/images/page1_executive.png`
- `docs/images/page2_attrition.png`
- `docs/images/page3_engagement.png`
- `docs/images/page4_diversity.png`
- `docs/images/page5_workforce.png`

## 9. Existing screenshots

Available screenshots:

- `copilot_narrative.png`
- `copilot_qa.png`
- `copilot_risk.png`
- `fairness_audit.png`
- `shap_summary.png`

Missing screenshots:

- All five Power BI page screenshots.

## 10. Current project state in 5 lines

1. The data foundation is strong: Day 1 lakehouse verification passes.
2. The ML layer is functional: Day 2 verification passes and risk outputs exist.
3. The governance/docs layer passes Day 4 verification.
4. The Copilot backend and Streamlit UI both start successfully.
5. The biggest visible gap is Power BI presentation completeness: five final dashboard screenshots are missing and the PBIX still has uncommitted local changes.

## 11. Day 1 verdict

Day 1 audit is complete enough to move into baseline recovery work.

The project is not broken. It is already functional, but it needs Power BI structure/polish, screenshot capture, and cleanup of uncommitted work before a clean v1-polished release.
