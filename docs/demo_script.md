# Demo Script — Agile HR Copilot

## 30-second elevator pitch

> I built a Fabric-inspired HR analytics accelerator that mirrors an HR Insights product:
> medallion lakehouse, Power BI semantic model, five CHRO dashboard pages, attrition-risk
> ML with SHAP explanations, and an AI Copilot that generates policy-grounded board
> narratives. It is governance-first: anonymised IDs, k-anonymity measures, fairness audit,
> model card, and human-in-the-loop decision support.

## Two-minute demo flow

### 0:00–0:20 — Context

Open the README. Frame the project:

> This is **Agile HR Copilot**, a compact people-analytics accelerator. It uses public
> IBM HR data plus synthetic monthly snapshots, recruitment, and engagement data.
> No real employee data is used.

### 0:20–0:45 — Lakehouse and semantic model

Switch to the architecture diagram in `docs/architecture.md`:

> Behind the scenes there is a bronze/silver/gold lakehouse stored as Parquet.
> The Gold layer is a star schema with employee, department, job role, and date
> dimensions feeding Power BI.

### 0:45–1:10 — Dashboards

Open Power BI. Navigate:

1. **Executive Overview** — headcount, attrition rate YoY, engagement index, high-risk count.
2. **Attrition & Retention** — risk band breakdown, top-driver bar, department heatmap.
3. Cross-filter the heatmap to show how risk concentrates in specific roles/tenure buckets.

### 1:10–1:40 — Copilot

Open Streamlit (`http://localhost:8501`):

1. **Board Narrative tab** — generate a CHRO narrative from the live KPIs.
2. **Policy Q&A tab** — ask: *"What does our retention policy say about stay interviews?"*.
   Highlight the cited source filenames and the chunk preview.
3. **Explain Attrition Risk tab** — pick a high-risk employee and read the plain-English
   explanation. Point out the top SHAP drivers.

### 1:40–2:00 — Governance

Show:

- `docs/model_card.md` — intended use and limitations.
- `docs/images/fairness_audit.png` — disparate impact ratios across Gender / AgeBand / Department.
- `docs/images/shap_summary.png` — global model behaviour.

Close with:

> Risk predictions are **decision support, not decision makers**. The next steps are to
> port this onto Fabric/OneLake, replace the local TF-IDF retriever with governed vector
> search, and wire the narrative generation into a Fabric-native Copilot workflow.

## Backup plan if something fails

| Failure | Fallback |
|---|---|
| Gemini API down | The Copilot returns a deterministic local narrative and TF-IDF excerpts. Demo continues. |
| Streamlit won't start | Show `scripts/smoke_day3_api.py` output instead. |
| Power BI can't refresh | Walk through the screenshots in `docs/images/`. |
| Lakehouse missing | Run `python scripts/day1_build_lakehouse.py` and `python scripts/day2_train_attrition_model.py`. |
