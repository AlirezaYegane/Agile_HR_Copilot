
Demo Script — Agile HR Copilot
30-second elevator pitch

I built a Fabric-inspired HR analytics accelerator that mirrors an HR Insights product: medallion lakehouse, Power BI semantic model, five CHRO dashboard pages, attrition-risk ML with SHAP explanations, and an AI Copilot that generates policy-grounded board narratives. It is governance-first: anonymised IDs, k-anonymity measures, fairness audit, model card, and human-in-the-loop decision support.

Two-minute demo flow
0:00–0:20 — Context

This is Agile HR Copilot, built as a compact people-analytics accelerator. It uses public IBM HR data plus synthetic monthly snapshots, recruitment, and engagement data. No real employee data is used.

0:20–0:45 — Lakehouse and semantic model

Behind the scenes there is a bronze/silver/gold lakehouse stored as Parquet. The Gold layer is a star schema with employee, department, job role, and date dimensions feeding Power BI.

0:45–1:10 — Dashboards

Show Executive Overview, then Attrition & Retention. Point to the risk heatmap, risk bands, and SHAP-driven employee-level top drivers.

1:10–1:40 — Copilot

Open Streamlit. Generate a board-ready narrative. Then ask a policy question and show the cited policy sources.

1:40–2:00 — Governance

Show the model card and fairness audit. Close by explaining that risk predictions are decision support, not decisions.
