
Interview Prep — Agile HR Copilot
1. Why did you build this?

I built this to show that I understand the shape of an HR Insights accelerator: lakehouse data foundation, semantic model, executive Power BI reporting, ML risk scoring, AI narratives, and governance. It is not just a dashboard; it is a working product slice.

2. Why medallion architecture?

Bronze keeps raw data with lineage, Silver cleans and anonymises it, and Gold turns it into a business-ready star schema. That maps cleanly to a Microsoft Fabric/OneLake-style implementation.

3. How realistic is the attrition model?

The model is useful as a demo of risk scoring and explainability, not as a production HR model. Production would need real temporal data, backtesting, fairness monitoring, and legal/privacy review.

4. How do you handle privacy?

No real employee data is used. IDs are anonymised, demographics are bucketed, demographic visuals use k-anonymity, and the model is framed as decision support only.

5. How does the Copilot avoid hallucination?

Policy Q&A is grounded in policy PDF chunks. The answer includes source metadata. If the context is insufficient, the assistant should refuse rather than invent.

6. What would you do next?

Port the lakehouse to Fabric OneLake/Delta, add row-level security, replace local TF-IDF with governed vector search, and integrate narrative generation into Power BI or Fabric-native workflows.
