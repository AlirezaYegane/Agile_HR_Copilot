# Interview Prep — Agile HR Copilot

## 1. Why did you build this?

I built this to demonstrate that I understand the shape of an HR Insights accelerator — lakehouse data foundation, semantic model, executive Power BI reporting, ML risk scoring, AI narratives, and governance — not just isolated dashboards. It is a working product slice that mirrors how a People Analytics solution would be delivered on Microsoft Fabric.

## 2. Why medallion architecture?

Bronze keeps the raw data with lineage, Silver cleans and anonymises it, and Gold turns it into a business-ready star schema. That layering keeps the source contract stable, the cleansing logic auditable, and the consumption layer reusable. It also maps cleanly to a Microsoft Fabric / OneLake / DirectLake-style implementation.

## 3. How realistic is the attrition model?

The model is useful as a **demo of risk scoring and explainability**, not as a production HR model. The IBM dataset is small and static, the time-series snapshots are synthetic, and attrition reasons are unknown. Production would need real temporal data, backtesting, drift monitoring, fairness monitoring at retraining cadence, and legal/privacy review.

## 4. How do you handle privacy?

- No real employee data is used.
- IDs are SHA-256 anonymised with a project salt.
- Demographics are bucketed (`AgeBand`, `SalaryBand`, `TenureCohort`).
- Demographic dashboards apply k-anonymity thresholds.
- The model is framed as decision support — never as an automated decision maker.

## 5. How does the Copilot avoid hallucination?

- **Policy Q&A** is grounded in TF-IDF retrieval over the policy PDFs. Every answer ships with the source filename and chunk preview.
- The prompt explicitly tells Gemini to refuse if the answer is not in the context.
- If Gemini is unavailable, the API returns the strongest TF-IDF excerpt as the answer rather than guessing.
- **Narrative** generation receives KPIs verbatim and is told not to invent numbers.

## 6. Why TF-IDF instead of embeddings?

Pragmatism. For a 4-day demo running locally, TF-IDF is robust, has zero external dependencies, and still grounds answers in the corpus. In production I would replace it with managed embeddings, governed vector search, and an evaluation harness for retrieval quality.

## 7. What does the fairness audit actually show?

It shows the **governance pattern**: measure, document, review. The audit reports high-risk prediction rates and disparate-impact ratios across Gender, AgeBand, and Department, plus ROC-AUC by group where class balance allows. The point isn't to declare the model safe — it's to demonstrate that group-level disparities would be caught and triaged before any deployment.

## 8. What would you do next?

- Port the lakehouse to Fabric OneLake / Delta with DirectLake.
- Add row-level security and Microsoft Purview sensitivity labels.
- Replace local TF-IDF with governed vector search.
- Add an automated retrieval-quality eval set.
- Integrate narrative generation into Power BI / Fabric-native Copilot workflows.
- Add survey free-text NLP and theme extraction for engagement.

## 9. What were the hardest design trade-offs?

- **Synthetic vs. real data.** Synthetic snapshots make the time-series story possible but limit how strong claims about model performance can be — so the model card and limitations section are explicit about it.
- **Embeddings vs. TF-IDF.** External embeddings looked slick but failed unpredictably. TF-IDF is less impressive on paper but more reliable in a live demo.
- **One model vs. two.** I shipped a Random Forest with a Logistic Regression baseline so the comparison is in the metrics file — useful for fairness review and for stakeholders who want a simpler, more interpretable challenger.
